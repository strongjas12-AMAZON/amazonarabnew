from fastapi import FastAPI, APIRouter, HTTPException, Depends, File, UploadFile, Form, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import logging
from pathlib import Path
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from supabase import create_client, Client
from io import BytesIO


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Supabase setup
SUPABASE_URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
SUPABASE_ANON_KEY = os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
SUPABASE_SERVICE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
ADMIN_SETUP_COMPLETE = os.environ.get('ADMIN_SETUP_COMPLETE', 'false').lower() == 'true'
ADMIN_CRYPTO_WALLET = os.environ.get('ADMIN_CRYPTO_WALLET', 'TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU')

# Create Supabase clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Security
security = HTTPBearer()

# Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["200/hour"])

# Create the main app
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

api_router = APIRouter(prefix="/api")

# Models
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = Field(..., pattern="^(buyer|seller)$")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class CreateProductRequest(BaseModel):
    title: str
    description: str
    price: float

class UpdateProductRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    images: Optional[List[str]] = None

class CreateOrderRequest(BaseModel):
    items: List[dict]
    totalAmount: float

class UpdateOrderStatusRequest(BaseModel):
    status: str
    
class VerificationDocumentRequest(BaseModel):
    documentType: str
    merchantInviteCode: Optional[str] = None

class ReviewVerificationRequest(BaseModel):
    status: str
    rejectionReason: Optional[str] = None


# Helper functions
def get_signed_document_url(file_path: str, expires_in: int = 3600) -> Optional[str]:
    """Generate signed URL for private document access (1 hour expiry)"""
    try:
        result = supabase_admin.storage.from_('documents').create_signed_url(
            file_path,
            expires_in
        )
        if result and 'signedURL' in result:
            return result['signedURL']
        return None
    except Exception as e:
        logging.error(f"Failed to generate signed URL for {file_path}: {str(e)}")
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        
        # Verify token with Supabase
        response = supabase.auth.get_user(token)
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user details from users table
        user_data = supabase_admin.table('users').select('*').eq('id', response.user.id).execute()
        
        if not user_data.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user_data.data[0]
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# Setup Admin Endpoint (One-time only)
@api_router.post("/setup-admin")
async def setup_admin():
    """Create admin account - runs only once"""
    global ADMIN_SETUP_COMPLETE
    
    if ADMIN_SETUP_COMPLETE:
        raise HTTPException(status_code=403, detail="Admin setup already complete")
    
    try:
        admin_email = "support@arabshopping.org"
        admin_password = "Hadi1247@"
        
        # Create auth user with admin client
        try:
            auth_response = supabase_admin.auth.admin.create_user({
                "email": admin_email,
                "password": admin_password,
                "email_confirm": True
            })
            user_id = auth_response.user.id
        except Exception as e:
            # If user already exists, get their ID
            existing = supabase_admin.table('users').select('id').eq('email', admin_email).execute()
            if existing.data:
                user_id = existing.data[0]['id']
            else:
                raise e
        
        # Create/update user in users table
        user_record = {
            'id': user_id,
            'email': admin_email,
            'name': 'Admin',
            'role': 'admin',
            'verificationStatus': 'verified',
            'createdAt': datetime.now(timezone.utc).isoformat()
        }
        
        # Upsert user
        supabase_admin.table('users').upsert(user_record).execute()
        
        # Update env flag
        env_path = ROOT_DIR / '.env'
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith('ADMIN_SETUP_COMPLETE'):
                    f.write('ADMIN_SETUP_COMPLETE=true\n')
                else:
                    f.write(line)
        
        ADMIN_SETUP_COMPLETE = True
        
        return {
            "success": True,
            "message": "Admin account created successfully",
            "email": admin_email
        }
    except Exception as e:
        logging.error(f"Admin setup error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Auth Routes
@api_router.post("/auth/register")
@limiter.limit("3/minute")  # 3 registrations per minute per IP
async def register(request: Request, req: RegisterRequest):
    """Register new user"""
    try:
        # Create auth user
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Registration failed")
        
        # Create user record
        user_data = {
            'id': auth_response.user.id,
            'email': req.email,
            'name': req.name,
            'role': req.role,
            'verificationStatus': 'unverified',
            'createdAt': datetime.now(timezone.utc).isoformat()
        }
        
        supabase_admin.table('users').insert(user_data).execute()
        
        return {
            "success": True,
            "user": user_data,
            "session": auth_response.session
        }
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/auth/login")
@limiter.limit("5/minute")  # 5 login attempts per minute per IP
async def login(request: Request, req: LoginRequest):
    """Login user"""
    try:
        # Sign in with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get user details
        user_data = supabase_admin.table('users').select('*').eq('id', auth_response.user.id).execute()
        
        if not user_data.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "user": user_data.data[0],
            "session": auth_response.session
        }
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


@api_router.post("/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user"""
    try:
        supabase.auth.sign_out()
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Product Routes
@api_router.get("/products")
async def get_products():
    """Get all verified products"""
    try:
        # Get products from verified sellers only
        products = supabase_admin.table('products').select('*, users!seller_id(name, verificationStatus)').execute()
        
        # Filter verified sellers
        verified_products = [p for p in products.data if p.get('users') and p['users'].get('verificationStatus') == 'verified']
        
        return {"success": True, "products": verified_products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/products/my")
async def get_my_products(current_user: dict = Depends(get_current_user)):
    """Get seller's own products"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can access this")
    
    try:
        products = supabase_admin.table('products').select('*').eq('sellerId', current_user['id']).execute()
        return {"success": True, "products": products.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/products")
async def create_product(request: CreateProductRequest, current_user: dict = Depends(get_current_user)):
    """Create new product"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can create products")
    
    if current_user['verificationStatus'] != 'verified':
        raise HTTPException(status_code=403, detail="Seller must be verified")
    
    try:
        product_data = {
            'id': str(uuid.uuid4()),
            'title': request.title,
            'description': request.description,
            'price': request.price,
            'images': [],
            'sellerId': current_user['id'],
            'createdAt': datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase_admin.table('products').insert(product_data).execute()
        return {"success": True, "product": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.put("/products/{product_id}")
async def update_product(product_id: str, request: UpdateProductRequest, current_user: dict = Depends(get_current_user)):
    """Update product"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can update products")
    
    try:
        # Verify ownership
        product = supabase_admin.table('products').select('*').eq('id', product_id).eq('sellerId', current_user['id']).execute()
        
        if not product.data:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        
        update_data = {}
        if request.title is not None:
            update_data['title'] = request.title
        if request.description is not None:
            update_data['description'] = request.description
        if request.price is not None:
            update_data['price'] = request.price
        if request.images is not None:
            update_data['images'] = request.images
        
        result = supabase_admin.table('products').update(update_data).eq('id', product_id).execute()
        return {"success": True, "product": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, current_user: dict = Depends(get_current_user)):
    """Delete product"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can delete products")
    
    try:
        # Verify ownership
        product = supabase_admin.table('products').select('*').eq('id', product_id).eq('sellerId', current_user['id']).execute()
        
        if not product.data:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        
        supabase_admin.table('products').delete().eq('id', product_id).execute()
        return {"success": True, "message": "Product deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/products/{product_id}/upload-image")
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload product image"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can upload images")
    
    try:
        # Verify ownership
        product = supabase_admin.table('products').select('*').eq('id', product_id).eq('sellerId', current_user['id']).execute()
        
        if not product.data:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        
        # Check image limit
        current_images = product.data[0].get('images', [])
        if len(current_images) >= 10:
            raise HTTPException(status_code=400, detail="Maximum 10 images allowed")
        
        # Read file
        contents = await file.read()
        
        # Upload to Supabase Storage
        file_ext = file.filename.split('.')[-1]
        file_name = f"{product_id}/{str(uuid.uuid4())}.{file_ext}"
        
        supabase_admin.storage.from_('products').upload(file_name, contents, {
            'content-type': file.content_type
        })
        
        # Get public URL
        public_url = supabase_admin.storage.from_('products').get_public_url(file_name)
        
        # Update product images
        updated_images = current_images + [public_url]
        supabase_admin.table('products').update({'images': updated_images}).eq('id', product_id).execute()
        
        return {"success": True, "imageUrl": public_url}
    except Exception as e:
        logging.error(f"Image upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Order Routes
@api_router.post("/orders")
@limiter.limit("10/hour")  # 10 orders per hour per IP
async def create_order(request: Request, req: CreateOrderRequest, current_user: dict = Depends(get_current_user)):
    """Create new order"""
    if current_user['role'] != 'buyer':
        raise HTTPException(status_code=403, detail="Only buyers can create orders")
    
    try:
        order_data = {
            'id': str(uuid.uuid4()),
            'buyerId': current_user['id'],
            'totalAmount': req.totalAmount,
            'paymentMethod': 'USDT_TRON',
            'paymentWallet': ADMIN_CRYPTO_WALLET,
            'paymentStatus': 'pending_payment',
            'confirmedByAdmin': False,
            'createdAt': datetime.now(timezone.utc).isoformat()
        }
        
        order_result = supabase_admin.table('orders').insert(order_data).execute()
        order_id = order_result.data[0]['id']
        
        # Create order items
        for item in req.items:
            item_data = {
                'id': str(uuid.uuid4()),
                'orderId': order_id,
                'productId': item['productId'],
                'quantity': item['quantity'],
                'price': item['price']
            }
            supabase_admin.table('order_items').insert(item_data).execute()
        
        return {"success": True, "order": order_result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/orders/my")
async def get_my_orders(current_user: dict = Depends(get_current_user)):
    """Get user's orders"""
    try:
        if current_user['role'] == 'buyer':
            orders = supabase_admin.table('orders').select('*, order_items(*, products(*))').eq('buyerId', current_user['id']).execute()
        elif current_user['role'] == 'seller':
            # Get orders containing seller's products
            orders = supabase_admin.table('orders').select('*, order_items(*, products(*))').execute()
            # Filter for seller's products
            filtered_orders = []
            for order in orders.data:
                seller_items = [item for item in order['order_items'] if item['products']['sellerId'] == current_user['id']]
                if seller_items:
                    order['order_items'] = seller_items
                    filtered_orders.append(order)
            return {"success": True, "orders": filtered_orders}
        elif current_user['role'] == 'admin':
            orders = supabase_admin.table('orders').select('*, order_items(*, products(*)), users!buyerId(name, email)').execute()
        else:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        return {"success": True, "orders": orders.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, request: UpdateOrderStatusRequest, current_user: dict = Depends(get_current_user)):
    """Update order status (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can update order status")
    
    try:
        update_data = {
            'paymentStatus': request.status
        }
        
        if request.status == 'paid':
            update_data['confirmedByAdmin'] = True
            update_data['confirmedAt'] = datetime.now(timezone.utc).isoformat()
        
        result = supabase_admin.table('orders').update(update_data).eq('id', order_id).execute()
        return {"success": True, "order": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Verification Routes
@api_router.post("/verification/upload")
async def upload_verification_document(
    documentType: str = Form(...),
    merchantInviteCode: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload verification document"""
    try:
        # For sellers, verify invite code
        if current_user['role'] == 'seller':
            if not merchantInviteCode:
                raise HTTPException(status_code=400, detail="Merchant invite code required for sellers")
            
            # Check if code exists and not used
            code_check = supabase_admin.table('merchant_invite_codes').select('*').eq('code', merchantInviteCode).eq('isUsed', False).execute()
            
            if not code_check.data:
                raise HTTPException(status_code=400, detail="Invalid or already used invite code")
        
        # Read file
        contents = await file.read()
        
        # Upload to Supabase Storage
        file_ext = file.filename.split('.')[-1]
        file_name = f"verification/{current_user['id']}/{str(uuid.uuid4())}.{file_ext}"
        
        supabase_admin.storage.from_('documents').upload(file_name, contents, {
            'content-type': file.content_type
        })
        
        # Get public URL
        public_url = supabase_admin.storage.from_('documents').get_public_url(file_name)
        
        # Create verification document record
        doc_data = {
            'id': str(uuid.uuid4()),
            'userId': current_user['id'],
            'documentType': documentType,
            'documentUrl': public_url,
            'status': 'pending',
            'merchantInviteCode': merchantInviteCode if current_user['role'] == 'seller' else None,
            'createdAt': datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase_admin.table('verification_documents').insert(doc_data).execute()
        
        # Update user status to pending
        supabase_admin.table('users').update({'verificationStatus': 'pending'}).eq('id', current_user['id']).execute()
        
        # Mark invite code as used if seller
        if current_user['role'] == 'seller' and merchantInviteCode:
            supabase_admin.table('merchant_invite_codes').update({
                'isUsed': True,
                'usedByUserId': current_user['id'],
                'usedAt': datetime.now(timezone.utc).isoformat()
            }).eq('code', merchantInviteCode).execute()
        
        return {"success": True, "document": result.data[0]}
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/verification/documents")
async def get_verification_documents(current_user: dict = Depends(get_current_user)):
    """Get verification documents with SIGNED URLs for private access"""
    try:
        if current_user['role'] == 'admin':
            # Admin sees all pending documents
            docs = supabase_admin.table('verification_documents').select('*, users(name, email, role)').eq('status', 'pending').execute()
        else:
            # Users see their own documents
            docs = supabase_admin.table('verification_documents').select('*').eq('userId', current_user['id']).execute()
        
        # Generate signed URLs for each document
        for doc in docs.data:
            if doc.get('documentUrl'):
                # Extract file path from public URL
                # Format: https://...supabase.co/storage/v1/object/public/documents/path/to/file.jpg
                if '/documents/' in doc['documentUrl']:
                    file_path = doc['documentUrl'].split('/documents/')[-1]
                    # Replace with signed URL (1 hour expiry)
                    signed_url = get_signed_document_url(file_path, expires_in=3600)
                    if signed_url:
                        doc['documentUrl'] = signed_url
                    else:
                        logging.warning(f"Failed to generate signed URL for document {doc['id']}")
        
        return {"success": True, "documents": docs.data}
    except Exception as e:
        logging.error(f"Failed to fetch verification documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/verification/documents/{doc_id}/review")
async def review_verification(doc_id: str, request: ReviewVerificationRequest, current_user: dict = Depends(get_current_user)):
    """Review verification document (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can review documents")
    
    try:
        # Get document
        doc = supabase_admin.table('verification_documents').select('*').eq('id', doc_id).execute()
        
        if not doc.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update document
        update_data = {
            'status': request.status,
            'reviewedAt': datetime.now(timezone.utc).isoformat()
        }
        
        if request.rejectionReason:
            update_data['rejectionReason'] = request.rejectionReason
        
        supabase_admin.table('verification_documents').update(update_data).eq('id', doc_id).execute()
        
        # Update user verification status
        user_id = doc.data[0]['userId']
        supabase_admin.table('users').update({'verificationStatus': request.status}).eq('id', user_id).execute()
        
        return {"success": True, "message": "Review completed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Admin Routes
@api_router.get("/admin/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        users = supabase_admin.table('users').select('*').execute()
        return {"success": True, "users": users.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/invite-codes")
async def create_invite_code(current_user: dict = Depends(get_current_user)):
    """Create merchant invite code (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        code = str(uuid.uuid4())[:8].upper()
        
        code_data = {
            'id': str(uuid.uuid4()),
            'code': code,
            'isUsed': False,
            'createdByAdmin': current_user['id'],
            'createdAt': datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase_admin.table('merchant_invite_codes').insert(code_data).execute()
        return {"success": True, "inviteCode": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/admin/invite-codes")
async def get_invite_codes(current_user: dict = Depends(get_current_user)):
    """Get all invite codes (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        codes = supabase_admin.table('merchant_invite_codes').select('*').execute()
        return {"success": True, "codes": codes.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return {"success": True, "user": current_user}


# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
