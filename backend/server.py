from fastapi import FastAPI, APIRouter, HTTPException, Depends, File, UploadFile, Form, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import logging
import asyncio
from pathlib import Path
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import uuid
from supabase import create_client, Client
import resend


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Supabase setup
SUPABASE_URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
SUPABASE_ANON_KEY = os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
SUPABASE_SERVICE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
ADMIN_SETUP_COMPLETE = os.environ.get('ADMIN_SETUP_COMPLETE', 'false').lower() == 'true'
ADMIN_CRYPTO_WALLET = os.environ.get('ADMIN_CRYPTO_WALLET', 'TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU')

# Email setup (Resend)
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'support@arabshopping.org')
ADMIN_EMAIL = 'support@arabshopping.org'

# Initialize Resend
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Create Supabase clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Security
security = HTTPBearer()

# Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["200/hour"])

# Predefined Product Categories
PRODUCT_CATEGORIES = [
    {"id": "electronics", "name": "Electronics & Gadgets", "icon": "📱"},
    {"id": "fashion", "name": "Fashion & Clothing", "icon": "👔"},
    {"id": "home", "name": "Home & Living", "icon": "🏠"},
    {"id": "beauty", "name": "Beauty & Health", "icon": "💄"},
    {"id": "food", "name": "Food & Beverages", "icon": "🍽️"},
    {"id": "jewelry", "name": "Jewelry & Watches", "icon": "💎"},
    {"id": "books", "name": "Books & Stationery", "icon": "📚"},
    {"id": "sports", "name": "Sports & Outdoors", "icon": "⚽"},
    {"id": "baby", "name": "Baby & Kids", "icon": "👶"},
    {"id": "automotive", "name": "Automotive", "icon": "🚗"},
]

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
    storeName: Optional[str] = None  # Required for sellers, optional for buyers

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class CreateProductRequest(BaseModel):
    title: str
    description: str
    price: float
    category: Optional[str] = None

class UpdateProductRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    images: Optional[List[str]] = None
    category: Optional[str] = None

class CreateOrderRequest(BaseModel):
    items: List[dict]
    totalAmount: float
    useWallet: Optional[bool] = False
    shippingAddressId: Optional[str] = None
    shippingName: Optional[str] = None
    shippingPhone: Optional[str] = None
    shippingAddress: Optional[dict] = None

class UpdateOrderStatusRequest(BaseModel):
    status: str
    
class VerificationDocumentRequest(BaseModel):
    documentType: str
    merchantInviteCode: Optional[str] = None

class ReviewVerificationRequest(BaseModel):
    status: str
    rejectionReason: Optional[str] = None


class StoreNameChangeRequest(BaseModel):
    newStoreName: str


class StoreNameChangeAdminAction(BaseModel):
    adminNote: Optional[str] = None


class CreatePayoutRequest(BaseModel):
    requestedAmount: float
    payoutWallet: str  # Required: USDT TRC20 wallet address


class UpdatePayoutStatusRequest(BaseModel):
    status: str
    adminNote: Optional[str] = None

class WalletRechargeRequest(BaseModel):
    amount: float
    paymentMethod: Optional[str] = 'USDT_TRON'
    paymentWallet: Optional[str] = None

class UpdateRechargeStatusRequest(BaseModel):
    status: str
    adminNote: Optional[str] = None

class CreateOrderWithWalletRequest(BaseModel):
    items: List[dict]
    totalAmount: float
    useWallet: bool = False

class CreateAddressRequest(BaseModel):
    fullName: str
    phone: str
    addressLine1: str
    addressLine2: Optional[str] = None
    city: str
    state: str
    postalCode: str
    country: str
    isDefault: Optional[bool] = False

class UpdateAddressRequest(BaseModel):
    fullName: Optional[str] = None
    phone: Optional[str] = None
    addressLine1: Optional[str] = None
    addressLine2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None
    isDefault: Optional[bool] = None

# ============================================================================
# ESCROW + DEPOSIT SYSTEM MODELS
# ============================================================================
class SellerDepositRequest(BaseModel):
    orderId: str
    amount: float

class SubmitUSDTDepositRequest(BaseModel):
    orderId: str
    transactionHash: str
    notes: Optional[str] = None

class ConfirmDepositRequest(BaseModel):
    approved: bool
    rejectionReason: Optional[str] = None

class ConfirmDeliveryRequest(BaseModel):
    orderId: str

class ShipByPlatformRequest(BaseModel):
    trackingNumber: Optional[str] = None
    courierName: Optional[str] = None

# Helper functions
def get_signed_document_url(file_path: str, expires_in: int = 3600) -> Optional[str]:
    """Generate signed URL for private document access (1 hour expiry)"""
    try:
        result = supabase_admin.storage.from_('documents').create_signed_url(
            file_path,
            expires_in
        )
        if result:
            if isinstance(result, dict) and 'signedURL' in result:
                return result['signedURL']
            if isinstance(result, dict) and 'signed_url' in result:
                return result['signed_url']
            if hasattr(result, 'data') and result.data:
                if isinstance(result.data, dict):
                    return result.data.get('signedUrl') or result.data.get('signedURL') or result.data.get('signed_url')
            if isinstance(result, str) and result.startswith('http'):
                return result
        logging.warning(f"Unexpected signed URL response format: {type(result)} - {result}")
        return None
    except Exception as e:
        logging.error(f"Failed to generate signed URL for {file_path}: {str(e)}")
        return None


def format_user_response(user_data: dict) -> dict:
    """Convert database fields to camelCase for frontend"""
    # Database uses snake_case: verification_status, created_at, ban_status, ban_reason, banned_by, banned_at, store_name
    return {
        'id': user_data.get('id'),
        'email': user_data.get('email'),
        'name': user_data.get('name'),
        'role': user_data.get('role'),
        'verificationStatus': user_data.get('verificationStatus') or user_data.get('verification_status') or 'unverified',
        'createdAt': user_data.get('createdAt') or user_data.get('created_at'),
        # Ban / suspension fields
        'banStatus': user_data.get('banStatus') or user_data.get('ban_status') or 'active',
        'banReason': user_data.get('banReason') or user_data.get('ban_reason'),
        'bannedBy': user_data.get('bannedBy') or user_data.get('banned_by'),
        'bannedAt': user_data.get('bannedAt') or user_data.get('banned_at'),
        # Store name (for sellers)
        'storeName': user_data.get('storeName') or user_data.get('store_name'),
    }


def format_product_response(product_data: dict) -> dict:
    """Convert snake_case DB fields to camelCase for frontend"""
    category_id = product_data.get('category')
    category_info = next((c for c in PRODUCT_CATEGORIES if c['id'] == category_id), None)
    store_name = product_data.get('storeName') or product_data.get('store_name')
    is_seller_product = product_data.get('isSellerProduct') or product_data.get('is_seller_product')
    if is_seller_product is None:
        is_seller_product = product_data.get('seller_id') is not None
    seller_name = product_data.get('seller_name')
    seller_verification = product_data.get('seller_verification_status') or product_data.get('sellerVerificationStatus')
    
    result = {
        'id': product_data.get('id'),
        'title': product_data.get('title'),
        'description': product_data.get('description'),
        'price': product_data.get('price'),
        'images': product_data.get('images', []),
        'sellerId': product_data.get('seller_id'),
        'category': category_id,
        'categoryName': category_info['name'] if category_info else None,
        'categoryIcon': category_info['icon'] if category_info else None,
        'isActive': product_data.get('is_active', True),  # Default to True if column doesn't exist
        'createdAt': product_data.get('created_at'),
        'isSellerProduct': bool(is_seller_product)
    }
    if store_name:
        result['storeName'] = store_name
    if 'users' in product_data and product_data['users']:
        result['users'] = {
            'name': product_data['users'].get('name'),
            'verificationStatus': product_data['users'].get('verificationStatus') or product_data['users'].get('verification_status') or 'unverified'
        }
        if store_name:
            result['users']['storeName'] = store_name
    elif store_name or seller_name or seller_verification:
        result['users'] = {
            'name': seller_name,
            'storeName': store_name,
            'verificationStatus': seller_verification or 'unverified'
        }
    return result


def format_order_response(order_data: dict) -> dict:
    """Convert snake_case DB fields to camelCase for frontend"""
    result = {
        'id': order_data.get('id'),
        'buyerId': order_data.get('buyer_id'),
        'totalAmount': order_data.get('total_amount'),
        'paymentMethod': order_data.get('payment_method'),
        'paymentWallet': order_data.get('payment_wallet'),
        'paymentStatus': order_data.get('payment_status'),
        'confirmedByAdmin': order_data.get('confirmed_by_admin'),
        'confirmedAt': order_data.get('confirmed_at'),
        'createdAt': order_data.get('created_at'),
        'escrowStatus': order_data.get('escrowStatus'),
        'depositRequired': order_data.get('depositRequired'),
        'depositInfo': order_data.get('depositInfo')
    }
    if 'users' in order_data and order_data['users']:
        result['users'] = {
            'name': order_data['users'].get('name'),
            'email': order_data['users'].get('email')
        }
    if 'order_items' in order_data:
        result['orderItems'] = []
        for item in order_data['order_items']:
            formatted_item = {
                'id': item.get('id'),
                'orderId': item.get('order_id'),
                'productId': item.get('product_id'),
                'quantity': item.get('quantity'),
                'price': item.get('price')
            }
            if 'products' in item and item['products']:
                formatted_item['product'] = format_product_response(item['products'])
            result['orderItems'].append(formatted_item)
    return result


def format_verification_doc_response(doc_data: dict) -> dict:
    """Convert snake_case DB fields to camelCase for frontend"""
    result = {
        'id': doc_data.get('id'),
        'userId': doc_data.get('user_id'),
        'documentType': doc_data.get('document_type'),
        'documentUrl': doc_data.get('document_url'),
        'status': doc_data.get('status'),
        'merchantInviteCode': doc_data.get('merchant_invite_code'),
        'rejectionReason': doc_data.get('rejection_reason'),
        'reviewedAt': doc_data.get('reviewed_at'),
        'createdAt': doc_data.get('created_at')
    }
    if 'users' in doc_data and doc_data['users']:
        result['users'] = {
            'name': doc_data['users'].get('name'),
            'email': doc_data['users'].get('email'),
            'role': doc_data['users'].get('role')
        }
    return result


def format_invite_code_response(code_data: dict) -> dict:
    """Convert snake_case DB fields to camelCase for frontend"""
    return {
        'id': code_data.get('id'),
        'code': code_data.get('code'),
        'isUsed': code_data.get('is_used'),
        'createdByAdmin': code_data.get('created_by_admin'),
        'usedByUserId': code_data.get('used_by_user_id'),
        'usedAt': code_data.get('used_at'),
        'createdAt': code_data.get('created_at')
    }


def format_payout_request_response(payout_data: dict) -> dict:
    """Convert payout_requests row to camelCase for frontend"""
    return {
        "id": payout_data.get("id"),
        "sellerId": payout_data.get("sellerId") or payout_data.get("seller_id"),
        "requestedAmount": float(payout_data.get("requestedAmount") or payout_data.get("requested_amount", 0)),
        "status": payout_data.get("status"),
        "payoutWallet": payout_data.get("payoutWallet") or payout_data.get("payout_wallet"),
        "requestDate": payout_data.get("requestDate") or payout_data.get("request_date"),
        "adminId": payout_data.get("adminId") or payout_data.get("admin_id"),
        "adminActionTimestamp": payout_data.get("adminActionTimestamp") or payout_data.get("admin_action_timestamp"),
        "adminNote": payout_data.get("adminNote") or payout_data.get("admin_note"),
        "createdAt": payout_data.get("createdAt") or payout_data.get("created_at"),
        "updatedAt": payout_data.get("updatedAt") or payout_data.get("updated_at"),
    }


def format_wallet_transaction_response(transaction_data: dict) -> dict:
    """Convert wallet_transactions row to camelCase for frontend"""
    return {
        "id": transaction_data.get("id"),
        "userId": transaction_data.get("userId") or transaction_data.get("user_id"),
        "userRole": transaction_data.get("userRole") or transaction_data.get("user_role"),
        "type": transaction_data.get("type"),
        "amount": float(transaction_data.get("amount", 0)),
        "previousBalance": float(transaction_data.get("previousBalance") or transaction_data.get("previous_balance", 0)),
        "newBalance": float(transaction_data.get("newBalance") or transaction_data.get("new_balance", 0)),
        "orderId": transaction_data.get("orderId") or transaction_data.get("order_id"),
        "rechargeRequestId": transaction_data.get("rechargeRequestId") or transaction_data.get("recharge_request_id"),
        "payoutRequestId": transaction_data.get("payoutRequestId") or transaction_data.get("payout_request_id"),
        "description": transaction_data.get("description"),
        "createdAt": transaction_data.get("createdAt") or transaction_data.get("created_at"),
    }


def format_wallet_recharge_request_response(recharge_data: dict) -> dict:
    """Convert wallet_recharge_requests row to camelCase for frontend"""
    return {
        "id": recharge_data.get("id"),
        "buyerId": recharge_data.get("buyerId") or recharge_data.get("buyer_id"),
        "amount": float(recharge_data.get("amount", 0)),
        "status": recharge_data.get("status"),
        "paymentMethod": recharge_data.get("paymentMethod") or recharge_data.get("payment_method"),
        "paymentWallet": recharge_data.get("paymentWallet") or recharge_data.get("payment_wallet"),
        "adminId": recharge_data.get("adminId") or recharge_data.get("admin_id"),
        "adminActionTimestamp": recharge_data.get("adminActionTimestamp") or recharge_data.get("admin_action_timestamp"),
        "adminNote": recharge_data.get("adminNote") or recharge_data.get("admin_note"),
        "createdAt": recharge_data.get("createdAt") or recharge_data.get("created_at"),
        "updatedAt": recharge_data.get("updatedAt") or recharge_data.get("updated_at"),
    }


async def get_or_create_buyer_wallet(user_id: str) -> dict:
    """Get or create buyer wallet"""
    wallet_result = supabase_admin.table('buyer_wallets').select('*').eq('userId', user_id).execute()
    if wallet_result.data:
        return wallet_result.data[0]
    # Create new wallet
    wallet_data = {
        'id': str(uuid.uuid4()),
        'userId': user_id,
        'balance': 0.00,
        'createdAt': datetime.now(timezone.utc).isoformat(),
        'updatedAt': datetime.now(timezone.utc).isoformat()
    }
    result = supabase_admin.table('buyer_wallets').insert(wallet_data).execute()
    return result.data[0] if result.data else wallet_data


async def get_or_create_seller_wallet(user_id: str) -> dict:
    """Get or create seller wallet"""
    wallet_result = supabase_admin.table('seller_wallets').select('*').eq('userId', user_id).execute()
    if wallet_result.data:
        return wallet_result.data[0]
    # Create new wallet
    wallet_data = {
        'id': str(uuid.uuid4()),
        'userId': user_id,
        'balance': 0.00,
        'totalEarnings': 0.00,
        'createdAt': datetime.now(timezone.utc).isoformat(),
        'updatedAt': datetime.now(timezone.utc).isoformat()
    }
    result = supabase_admin.table('seller_wallets').insert(wallet_data).execute()
    return result.data[0] if result.data else wallet_data


async def create_wallet_transaction(
    user_id: str,
    user_role: str,
    transaction_type: str,
    amount: float,
    previous_balance: float,
    new_balance: float,
    order_id: Optional[str] = None,
    recharge_request_id: Optional[str] = None,
    payout_request_id: Optional[str] = None,
    description: Optional[str] = None
):
    """Create a wallet transaction record"""
    transaction_data = {
        'id': str(uuid.uuid4()),
        'userId': user_id,
        'userRole': user_role,
        'type': transaction_type,
        'amount': amount,
        'previousBalance': previous_balance,
        'newBalance': new_balance,
        'orderId': order_id,
        'rechargeRequestId': recharge_request_id,
        'payoutRequestId': payout_request_id,
        'description': description,
        'createdAt': datetime.now(timezone.utc).isoformat()
    }
    supabase_admin.table('wallet_transactions').insert(transaction_data).execute()


# Email notification functions
async def send_email_async(to_email: str, subject: str, html_content: str):
    """Send email asynchronously using Resend"""
    if not RESEND_API_KEY:
        logging.warning("RESEND_API_KEY not configured, skipping email")
        return None
    
    try:
        params = {
            "from": f"Amazon Arab <{SENDER_EMAIL}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        result = await asyncio.to_thread(resend.Emails.send, params)
        logging.info(f"Email sent to {to_email}: {result.get('id')}")
        return result
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {str(e)}")
        return None


def get_email_template(template_type: str, data: dict) -> tuple:
    """Generate email subject and HTML content based on template type"""
    
    if template_type == "order_placed_buyer":
        subject = f"Order Confirmed - #{data['order_id'][:8].upper()}"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1a1a1a; color: #fff; padding: 20px;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37;">
                <h1 style="color: #D4AF37; margin: 0;">Amazon Arab</h1>
            </div>
            <div style="padding: 30px 20px;">
                <h2 style="color: #D4AF37;">Thank you for your order!</h2>
                <p>Hi {data['buyer_name']},</p>
                <p>Your order has been placed successfully. Please complete the payment to proceed.</p>
                
                <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #D4AF37; margin-top: 0;">Order Details</h3>
                    <p><strong>Order ID:</strong> #{data['order_id'][:8].upper()}</p>
                    <p><strong>Total Amount:</strong> ${data['total_amount']:.2f}</p>
                    <p><strong>Payment Method:</strong> USDT (TRC20)</p>
                </div>
                
                <div style="background: #D4AF37; color: #000; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Payment Instructions</h3>
                    <p><strong>Send exactly ${data['total_amount']:.2f} USDT to:</strong></p>
                    <p style="font-family: monospace; background: #fff; padding: 10px; border-radius: 4px; word-break: break-all;">
                        {data['wallet_address']}
                    </p>
                    <p style="font-size: 12px;">Network: TRC20 (Tron)</p>
                </div>
                
                <p style="color: #888;">Once payment is confirmed, we'll update your order status.</p>
            </div>
            <div style="text-align: center; padding: 20px; border-top: 1px solid #333; color: #666; font-size: 12px;">
                <p>© 2026 Amazon Arab. All rights reserved.</p>
            </div>
        </div>
        """
        return subject, html
    
    elif template_type == "payment_confirmed_buyer":
        subject = f"Payment Confirmed - Order #{data['order_id'][:8].upper()}"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1a1a1a; color: #fff; padding: 20px;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37;">
                <h1 style="color: #D4AF37; margin: 0;">Amazon Arab</h1>
            </div>
            <div style="padding: 30px 20px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <span style="font-size: 48px;">✅</span>
                </div>
                <h2 style="color: #4CAF50; text-align: center;">Payment Confirmed!</h2>
                <p>Hi {data['buyer_name']},</p>
                <p>Great news! Your payment has been confirmed by our team.</p>
                
                <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #D4AF37; margin-top: 0;">Order Summary</h3>
                    <p><strong>Order ID:</strong> #{data['order_id'][:8].upper()}</p>
                    <p><strong>Total Paid:</strong> ${data['total_amount']:.2f}</p>
                    <p><strong>Status:</strong> <span style="color: #4CAF50;">PAID</span></p>
                </div>
                
                <p>The seller has been notified and will process your order soon.</p>
                <p style="color: #888;">Thank you for shopping with Amazon Arab!</p>
            </div>
            <div style="text-align: center; padding: 20px; border-top: 1px solid #333; color: #666; font-size: 12px;">
                <p>© 2026 Amazon Arab. All rights reserved.</p>
            </div>
        </div>
        """
        return subject, html
    
    elif template_type == "new_order_seller":
        subject = f"New Order Received - #{data['order_id'][:8].upper()}"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1a1a1a; color: #fff; padding: 20px;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37;">
                <h1 style="color: #D4AF37; margin: 0;">Amazon Arab</h1>
            </div>
            <div style="padding: 30px 20px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <span style="font-size: 48px;">🛒</span>
                </div>
                <h2 style="color: #D4AF37; text-align: center;">New Order Received!</h2>
                <p>Hi {data['seller_name']},</p>
                <p>You have received a new order for your product(s).</p>
                
                <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #D4AF37; margin-top: 0;">Order Details</h3>
                    <p><strong>Order ID:</strong> #{data['order_id'][:8].upper()}</p>
                    <p><strong>Product:</strong> {data['product_title']}</p>
                    <p><strong>Quantity:</strong> {data['quantity']}</p>
                    <p><strong>Amount:</strong> ${data['item_total']:.2f}</p>
                    <p><strong>Status:</strong> <span style="color: #FFA500;">Pending Payment</span></p>
                </div>
                
                <p>You will be notified once the buyer completes the payment.</p>
                <p style="color: #888;">Log in to your seller dashboard to view order details.</p>
            </div>
            <div style="text-align: center; padding: 20px; border-top: 1px solid #333; color: #666; font-size: 12px;">
                <p>© 2026 Amazon Arab. All rights reserved.</p>
            </div>
        </div>
        """
        return subject, html
    
    elif template_type == "new_order_admin":
        subject = f"[Admin] New Order - #{data['order_id'][:8].upper()}"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1a1a1a; color: #fff; padding: 20px;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37;">
                <h1 style="color: #D4AF37; margin: 0;">Amazon Arab - Admin</h1>
            </div>
            <div style="padding: 30px 20px;">
                <h2 style="color: #D4AF37;">New Order Notification</h2>
                
                <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #D4AF37; margin-top: 0;">Order Details</h3>
                    <p><strong>Order ID:</strong> #{data['order_id'][:8].upper()}</p>
                    <p><strong>Buyer:</strong> {data['buyer_name']} ({data['buyer_email']})</p>
                    <p><strong>Total Amount:</strong> ${data['total_amount']:.2f}</p>
                    <p><strong>Payment Wallet:</strong></p>
                    <p style="font-family: monospace; background: #333; padding: 5px; font-size: 12px;">{data['wallet_address']}</p>
                </div>
                
                <p>Please monitor for incoming payment and confirm when received.</p>
            </div>
            <div style="text-align: center; padding: 20px; border-top: 1px solid #333; color: #666; font-size: 12px;">
                <p>© 2026 Amazon Arab. All rights reserved.</p>
            </div>
        </div>
        """
        return subject, html
    
    elif template_type == "order_completed_buyer":
        subject = f"Order Completed - #{data['order_id'][:8].upper()}"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1a1a1a; color: #fff; padding: 20px;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37;">
                <h1 style="color: #D4AF37; margin: 0;">Amazon Arab</h1>
            </div>
            <div style="padding: 30px 20px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <span style="font-size: 48px;">🎉</span>
                </div>
                <h2 style="color: #4CAF50; text-align: center;">Order Completed!</h2>
                <p>Hi {data['buyer_name']},</p>
                <p>Great news! Your order has been fulfilled and marked as complete.</p>
                
                <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #D4AF37; margin-top: 0;">Order Summary</h3>
                    <p><strong>Order ID:</strong> #{data['order_id'][:8].upper()}</p>
                    <p><strong>Total Amount:</strong> ${data['total_amount']:.2f}</p>
                    <p><strong>Status:</strong> <span style="color: #4CAF50;">✓ COMPLETED</span></p>
                </div>
                
                <p>Thank you for shopping with us! We hope you enjoy your purchase.</p>
                <p style="color: #888;">If you have any questions about your order, please contact our support team.</p>
                
                <div style="text-align: center; margin-top: 30px;">
                    <p style="color: #D4AF37;">We'd love to see you again!</p>
                </div>
            </div>
            <div style="text-align: center; padding: 20px; border-top: 1px solid #333; color: #666; font-size: 12px;">
                <p>© 2026 Amazon Arab. All rights reserved.</p>
            </div>
        </div>
        """
        return subject, html
    
    elif template_type == "order_completed_seller":
        subject = f"Order Fulfilled - #{data['order_id'][:8].upper()}"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1a1a1a; color: #fff; padding: 20px;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37;">
                <h1 style="color: #D4AF37; margin: 0;">Amazon Arab</h1>
            </div>
            <div style="padding: 30px 20px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <span style="font-size: 48px;">✅</span>
                </div>
                <h2 style="color: #4CAF50; text-align: center;">Order Marked Complete</h2>
                <p>Hi {data['seller_name']},</p>
                <p>The following order has been marked as completed by the admin.</p>
                
                <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #D4AF37; margin-top: 0;">Order Details</h3>
                    <p><strong>Order ID:</strong> #{data['order_id'][:8].upper()}</p>
                    <p><strong>Product:</strong> {data['product_title']}</p>
                    <p><strong>Quantity:</strong> {data['quantity']}</p>
                    <p><strong>Amount:</strong> ${data['item_total']:.2f}</p>
                    <p><strong>Status:</strong> <span style="color: #4CAF50;">✓ COMPLETED</span></p>
                </div>
                
                <p style="color: #888;">Great job! Keep up the excellent work.</p>
            </div>
            <div style="text-align: center; padding: 20px; border-top: 1px solid #333; color: #666; font-size: 12px;">
                <p>© 2026 Amazon Arab. All rights reserved.</p>
            </div>
        </div>
        """
        return subject, html
    
    elif template_type == "verification_approved":
        subject = "🎉 Verification Approved - Welcome to Amazon Arab!"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1a1a1a; color: #fff; padding: 20px;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37;">
                <h1 style="color: #D4AF37; margin: 0;">Amazon Arab</h1>
            </div>
            <div style="padding: 30px 20px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <span style="font-size: 48px;">🎉</span>
                </div>
                <h2 style="color: #4CAF50; text-align: center;">Verification Approved!</h2>
                <p>Hi {data['user_name']},</p>
                <p>Congratulations! Your account has been verified and you're now ready to start selling on Amazon Arab.</p>
                
                <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #D4AF37; margin-top: 0;">What's Next?</h3>
                    <ul style="padding-left: 20px; line-height: 1.8;">
                        <li>Log in to your Seller Dashboard</li>
                        <li>Add your first product</li>
                        <li>Start receiving orders from buyers</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="color: #D4AF37; font-size: 18px;">Welcome to the Amazon Arab family!</p>
                </div>
                
                <p style="color: #888;">If you have any questions, feel free to contact our support team.</p>
            </div>
            <div style="text-align: center; padding: 20px; border-top: 1px solid #333; color: #666; font-size: 12px;">
                <p>© 2026 Amazon Arab. All rights reserved.</p>
            </div>
        </div>
        """
        return subject, html
    
    elif template_type == "verification_rejected":
        subject = "Verification Update - Action Required"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1a1a1a; color: #fff; padding: 20px;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37;">
                <h1 style="color: #D4AF37; margin: 0;">Amazon Arab</h1>
            </div>
            <div style="padding: 30px 20px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <span style="font-size: 48px;">📋</span>
                </div>
                <h2 style="color: #FFA500; text-align: center;">Verification Requires Attention</h2>
                <p>Hi {data['user_name']},</p>
                <p>We've reviewed your verification documents and unfortunately, we couldn't approve them at this time.</p>
                
                <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #FFA500;">
                    <h3 style="color: #D4AF37; margin-top: 0;">Reason</h3>
                    <p>{data.get('rejection_reason', 'Please ensure your documents are clear, valid, and match our requirements.')}</p>
                </div>
                
                <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #D4AF37; margin-top: 0;">What You Can Do</h3>
                    <ul style="padding-left: 20px; line-height: 1.8;">
                        <li>Review the rejection reason above</li>
                        <li>Prepare new, clear documents</li>
                        <li>Log in and submit your documents again</li>
                        <li>Contact support if you need assistance</li>
                    </ul>
                </div>
                
                <p style="color: #888;">We're here to help you succeed. Don't hesitate to reach out if you have questions.</p>
            </div>
            <div style="text-align: center; padding: 20px; border-top: 1px solid #333; color: #666; font-size: 12px;">
                <p>© 2026 Amazon Arab. All rights reserved.</p>
            </div>
        </div>
        """
        return subject, html
    
    return "", ""


async def send_order_notifications(order_data: dict, order_items: list, notification_type: str = "order_placed"):
    """Send all relevant notifications for an order"""
    try:
        # Get buyer info
        buyer = supabase_admin.table('users').select('*').eq('id', order_data['buyer_id']).execute()
        buyer_info = buyer.data[0] if buyer.data else {}
        
        if notification_type == "order_placed":
            # 1. Send to buyer
            subject, html = get_email_template("order_placed_buyer", {
                'order_id': order_data['id'],
                'buyer_name': buyer_info.get('name', 'Customer'),
                'total_amount': float(order_data['total_amount']),
                'wallet_address': order_data['payment_wallet']
            })
            await send_email_async(buyer_info.get('email'), subject, html)
            await asyncio.sleep(0.6)  # Rate limit: 2 req/sec
            
            # 2. Send to each seller
            for item in order_items:
                product = supabase_admin.table('products').select('*, users!seller_id(*)').eq('id', item['product_id']).execute()
                if product.data:
                    prod = product.data[0]
                    seller_info = prod.get('users', {})
                    if seller_info and seller_info.get('email'):
                        subject, html = get_email_template("new_order_seller", {
                            'order_id': order_data['id'],
                            'seller_name': seller_info.get('name', 'Seller'),
                            'product_title': prod.get('title', 'Product'),
                            'quantity': item['quantity'],
                            'item_total': float(item['price']) * item['quantity']
                        })
                        await send_email_async(seller_info.get('email'), subject, html)
                        await asyncio.sleep(0.6)  # Rate limit: 2 req/sec
            
            # 3. Send to admin
            subject, html = get_email_template("new_order_admin", {
                'order_id': order_data['id'],
                'buyer_name': buyer_info.get('name', 'Customer'),
                'buyer_email': buyer_info.get('email', ''),
                'total_amount': float(order_data['total_amount']),
                'wallet_address': order_data['payment_wallet']
            })
            await send_email_async(ADMIN_EMAIL, subject, html)
            
        elif notification_type == "payment_confirmed":
            # Send payment confirmation to buyer
            subject, html = get_email_template("payment_confirmed_buyer", {
                'order_id': order_data['id'],
                'buyer_name': buyer_info.get('name', 'Customer'),
                'total_amount': float(order_data['total_amount'])
            })
            await send_email_async(buyer_info.get('email'), subject, html)
        
        elif notification_type == "order_completed":
            # 1. Send completion notification to buyer
            subject, html = get_email_template("order_completed_buyer", {
                'order_id': order_data['id'],
                'buyer_name': buyer_info.get('name', 'Customer'),
                'total_amount': float(order_data['total_amount'])
            })
            await send_email_async(buyer_info.get('email'), subject, html)
            await asyncio.sleep(0.6)  # Rate limit
            
            # 2. Get order items and notify sellers
            order_items_result = supabase_admin.table('order_items').select('*, products(*, users!seller_id(*))').eq('order_id', order_data['id']).execute()
            
            notified_sellers = set()  # Track notified sellers to avoid duplicates
            for item in order_items_result.data:
                product = item.get('products', {})
                seller_info = product.get('users', {})
                seller_email = seller_info.get('email')
                
                if seller_email and seller_email not in notified_sellers:
                    subject, html = get_email_template("order_completed_seller", {
                        'order_id': order_data['id'],
                        'seller_name': seller_info.get('name', 'Seller'),
                        'product_title': product.get('title', 'Product'),
                        'quantity': item.get('quantity', 1),
                        'item_total': float(item.get('price', 0)) * item.get('quantity', 1)
                    })
                    await send_email_async(seller_email, subject, html)
                    notified_sellers.add(seller_email)
                    await asyncio.sleep(0.6)  # Rate limit
            
    except Exception as e:
        logging.error(f"Failed to send order notifications: {str(e)}")


async def send_verification_email(user_id: str, status: str, rejection_reason: str = None):
    """Send verification approval/rejection email to user"""
    try:
        # Get user info
        user = supabase_admin.table('users').select('*').eq('id', user_id).execute()
        if not user.data:
            logging.error(f"User not found for verification email: {user_id}")
            return
        
        user_info = user.data[0]
        
        if status == 'verified':
            subject, html = get_email_template("verification_approved", {
                'user_name': user_info.get('name', 'Seller')
            })
        elif status == 'rejected':
            subject, html = get_email_template("verification_rejected", {
                'user_name': user_info.get('name', 'Seller'),
                'rejection_reason': rejection_reason or 'Please ensure your documents are clear, valid, and match our requirements.'
            })
        else:
            return
        
        await send_email_async(user_info.get('email'), subject, html)
        
    except Exception as e:
        logging.error(f"Failed to send verification email: {str(e)}")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token.

    Also enforces ban / suspension:
    - Users with ban_status = 'banned' or 'suspended' are rejected with 403.
    """
    try:
        token = credentials.credentials

        response = supabase.auth.get_user(token)
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_result = supabase_admin.table('users').select('*').eq('id', response.user.id).execute()

        if not user_result.data:
            raise HTTPException(status_code=404, detail="User not found")

        db_user = user_result.data[0]
        ban_status = db_user.get('ban_status') or db_user.get('banStatus') or 'active'
        if ban_status in ('banned', 'suspended'):
            # Optional: include generic message without exposing too many details
            raise HTTPException(status_code=403, detail="Your account is not allowed to perform this action.")

        return format_user_response(db_user)
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
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
        user_id = None
        
        # First check if user exists in our users table
        existing_user = supabase_admin.table('users').select('id').eq('email', admin_email).execute()
        if existing_user.data:
            user_id = existing_user.data[0]['id']
        else:
            # Try to create new auth user
            try:
                auth_response = supabase_admin.auth.admin.create_user({
                    "email": admin_email,
                    "password": admin_password,
                    "email_confirm": True
                })
                user_id = auth_response.user.id
            except Exception as auth_error:
                # User exists in auth but not in users table - get their ID via login
                error_msg = str(auth_error)
                if "already been registered" in error_msg:
                    # Sign in to get the user ID
                    try:
                        login_response = supabase_admin.auth.sign_in_with_password({
                            "email": admin_email,
                            "password": admin_password
                        })
                        user_id = login_response.user.id
                    except:
                        # List all auth users and find the admin
                        users_list = supabase_admin.auth.admin.list_users()
                        for u in users_list:
                            if u.email == admin_email:
                                user_id = u.id
                                break
                if not user_id:
                    raise auth_error
        
        user_record = {
            'id': user_id,
            'email': admin_email,
            'name': 'Admin',
            'role': 'admin',
            'verification_status': 'verified'  # Database column is verification_status (snake_case)
            # Note: created_at has DEFAULT NOW() in schema, so we don't need to set it explicitly
        }
        
        supabase_admin.table('users').upsert(user_record).execute()
        
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


# Development endpoint to create test users
@api_router.post("/setup-test-users")
async def setup_test_users():
    """Create test seller and buyer accounts for development - uses existing auth users from Supabase"""
    try:
        created_users = []
        
        # Define test users to create in our users table
        # These should already exist in Supabase Auth (created via dashboard or previously)
        test_users = [
            {
                'email': 'testseller@test.com',
                'name': 'Test Seller',
                'role': 'seller',
                'verificationStatus': 'verified'  # Pre-verified for testing
            },
            {
                'email': 'testbuyer@test.com', 
                'name': 'Test Buyer',
                'role': 'buyer',
                'verificationStatus': 'unverified'
            }
        ]
        
        for test_user in test_users:
            # Check if already exists in our users table
            existing = supabase_admin.table('users').select('id').eq('email', test_user['email']).execute()
            if existing.data:
                created_users.append({'email': test_user['email'], 'status': 'already exists'})
                continue
            
            # Try to find user in Supabase Auth or create new one
            user_id = None
            try:
                # Try to create new auth user
                auth_response = supabase_admin.auth.admin.create_user({
                    "email": test_user['email'],
                    "password": "TestPass123!",
                    "email_confirm": True
                })
                user_id = auth_response.user.id
            except Exception as auth_error:
                error_msg = str(auth_error)
                if "already been registered" in error_msg:
                    # User exists in auth - try to get their ID by listing users
                    try:
                        users_list = supabase_admin.auth.admin.list_users()
                        for u in users_list:
                            if u.email == test_user['email']:
                                user_id = u.id
                                break
                    except:
                        pass
                
                if not user_id:
                    created_users.append({
                        'email': test_user['email'], 
                        'status': f'failed: {str(auth_error)[:100]}'
                    })
                    continue
            
            # Create user record in our table
            user_record = {
                'id': user_id,
                'email': test_user['email'],
                'name': test_user['name'],
                'role': test_user['role'],
                'verification_status': test_user['verificationStatus']  # Database column is verification_status (snake_case)
                # Note: created_at has DEFAULT NOW() in schema, so we don't need to set it explicitly
            }
            
            supabase_admin.table('users').insert(user_record).execute()
            created_users.append({
                'email': test_user['email'],
                'status': 'created',
                'role': test_user['role']
            })
        
        return {
            "success": True,
            "message": "Test users setup complete",
            "users": created_users,
            "credentials": {
                "seller": {"email": "testseller@test.com", "password": "TestPass123!"},
                "buyer": {"email": "testbuyer@test.com", "password": "TestPass123!"}
            }
        }
    except Exception as e:
        logging.error(f"Test users setup error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Auth Routes
@api_router.post("/auth/register")
@limiter.limit("3/minute")
async def register(request: Request, req: RegisterRequest):
    """Register new user"""
    try:
        # Validate store name for sellers
        if req.role == 'seller':
            if not req.storeName or not req.storeName.strip():
                raise HTTPException(status_code=400, detail="Store name is required for sellers")
            
            store_name = req.storeName.strip()
            
            # Validate store name length
            if len(store_name) < 2:
                raise HTTPException(status_code=400, detail="Store name must be at least 2 characters")
            if len(store_name) > 100:
                raise HTTPException(status_code=400, detail="Store name must be less than 100 characters")
            
            # Check if store name already exists
            existing_store = supabase_admin.table('users').select('id, email').eq('store_name', store_name).execute()
            if existing_store.data:
                raise HTTPException(status_code=400, detail="Store name already taken. Please choose a different name.")
        
        # Use admin client to create user (bypasses email confirmation)
        try:
            auth_response = supabase_admin.auth.admin.create_user({
                "email": req.email,
                "password": req.password,
                "email_confirm": True  # Auto-confirm email
            })
            user_id = auth_response.user.id
        except Exception as auth_error:
            # If user creation fails, try regular signup
            logging.warning(f"Admin create_user failed, trying regular signup: {str(auth_error)}")
            auth_response = supabase.auth.sign_up({
                "email": req.email,
                "password": req.password
            })
            if not auth_response.user:
                raise HTTPException(status_code=400, detail="Registration failed")
            user_id = auth_response.user.id
        
        user_data = {
            'id': user_id,
            'email': req.email,
            'name': req.name,
            'role': req.role,
            'verification_status': 'unverified'  # Database column is verification_status (snake_case)
            # Note: created_at has DEFAULT NOW() in schema, so we don't need to set it explicitly
        }
        
        # Add store_name for sellers only
        if req.role == 'seller' and req.storeName:
            user_data['store_name'] = req.storeName.strip()
        
        supabase_admin.table('users').insert(user_data).execute()
        
        # Create a session for the user by signing them in
        try:
            login_response = supabase.auth.sign_in_with_password({
                "email": req.email,
                "password": req.password
            })
            session = login_response.session
        except:
            session = None
        
        return {
            "success": True,
            "user": format_user_response(user_data),
            "session": session
        }
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, req: LoginRequest):
    """Login user"""
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_result = supabase_admin.table('users').select('*').eq('id', auth_response.user.id).execute()

        if not user_result.data:
            raise HTTPException(status_code=404, detail="User not found")

        db_user = user_result.data[0]
        ban_status = db_user.get('ban_status') or db_user.get('banStatus') or 'active'
        if ban_status in ('banned', 'suspended'):
            # Do not issue a session for banned / suspended users
            if ban_status == 'banned':
                detail = "Your account has been banned. Please contact support."
            else:
                detail = "Your account has been temporarily suspended. Please contact support."
            raise HTTPException(status_code=403, detail=detail)

        return {
            "success": True,
            "user": format_user_response(db_user),
            "session": auth_response.session
        }
    except HTTPException as exc:
        # Re-raise HTTP-related errors (invalid credentials, banned, user not found)
        raise exc
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


class BanUserRequest(BaseModel):
    status: str = Field(..., pattern="^(banned|suspended)$")
    reason: str


@api_router.post("/admin/users/{user_id}/ban")
async def ban_user(user_id: str, request: BanUserRequest, current_user: dict = Depends(get_current_user)):
    """Ban or suspend a user (admin only)."""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        # Ensure target user exists
        user_result = supabase_admin.table('users').select('*').eq('id', user_id).execute()
        if not user_result.data:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = {
            'ban_status': request.status,
            'ban_reason': request.reason,
            'banned_by': current_user['id'],
            'banned_at': datetime.now(timezone.utc).isoformat(),
        }

        updated = supabase_admin.table('users').update(update_data).eq('id', user_id).execute()
        return {"success": True, "user": format_user_response(updated.data[0])}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/admin/users/{user_id}/unban")
async def unban_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Remove ban / suspension from a user (admin only)."""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        user_result = supabase_admin.table('users').select('*').eq('id', user_id).execute()
        if not user_result.data:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = {
            'ban_status': 'active',
            'ban_reason': None,
            'banned_by': None,
            'banned_at': None,
        }

        updated = supabase_admin.table('users').update(update_data).eq('id', user_id).execute()
        return {"success": True, "user": format_user_response(updated.data[0])}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Product Routes
@api_router.get("/categories")
async def get_categories():
    """Get all product categories"""
    return {"success": True, "categories": PRODUCT_CATEGORIES}


@api_router.get("/products")
async def get_products(category: Optional[str] = None, search: Optional[str] = None):
    """Get marketplace products from NEW store system that sellers have added (buyer-facing)."""
    try:
        search_term = (search or "").strip()
        
        # Query store_products (NEW SYSTEM) with catalog and store info
        query = supabase_admin.table('store_products') \
            .select('*, product_catalog!inner(*), stores!inner(id, store_name, seller_id, status)') \
            .eq('is_active', True) \
            .eq('stores.status', 'active')

        store_products_result = query.order('created_at', desc=True).execute()

        products = []
        search_lower = search_term.lower() if search_term else None

        for sp in store_products_result.data or []:
            catalog_product = sp.get('product_catalog') or {}
            store_info = sp.get('stores') or {}
            
            if not catalog_product:
                continue
                
            # Filter by category if provided
            if category and catalog_product.get('category') != category:
                continue

            store_name = store_info.get('store_name', '').strip()
            product_name = catalog_product.get('name', '')
            product_desc = catalog_product.get('description', '')

            # Search filter - check store name, product name, and description
            if search_lower:
                if search_lower not in store_name.lower() and \
                   search_lower not in product_name.lower() and \
                   search_lower not in product_desc.lower():
                    continue

            # Build product response
            merged_product = {
                'id': sp.get('id'),  # store_product id
                'title': catalog_product.get('name'),
                'description': catalog_product.get('description'),
                'price': sp.get('price'),  # Seller's custom price
                'category': catalog_product.get('category'),
                'images': catalog_product.get('images', []),
                'stock': sp.get('stock_quantity', 0),
                'store_name': store_name,
                'seller_id': store_info.get('seller_id'),
                'store_id': store_info.get('id'),
                'is_active': sp.get('is_active', True),
                'added_at': sp.get('created_at'),
                'catalog_product_id': sp.get('catalog_product_id')
            }
            products.append(merged_product)

        return {"success": True, "products": products}
    except Exception as e:
        logging.error(f"Get products error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/products/my")
async def get_my_products(current_user: dict = Depends(get_current_user)):
    """Get seller's selected products from catalog"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can access this")
    
    try:
        seller_products = supabase_admin.table('seller_products') \
            .select('*, products(*)') \
            .eq('seller_id', current_user['id']) \
            .eq('is_active', True) \
            .execute()

        if not seller_products.data:
            return {"success": True, "products": []}

        products = []
        for sp in seller_products.data:
            product_data = sp.get('products') or {}
            if not product_data:
                continue
            if product_data.get('is_active') is False:
                continue

            merged_product = {
                **product_data,
                'store_name': sp.get('store_name'),
                'is_seller_product': sp.get('is_seller_product'),
                'seller_id': sp.get('seller_id') or product_data.get('seller_id'),
                'seller_name': current_user.get('name'),
                'seller_verification_status': current_user.get('verificationStatus') or current_user.get('verification_status')
            }
            products.append(format_product_response(merged_product))

        return {"success": True, "products": products}
    except Exception as e:
        logging.error(f"Get my products error: {str(e)}")
        # Fallback: if seller_products table doesn't exist yet, return empty
        if "seller_products" in str(e):
            return {"success": True, "products": []}
        raise HTTPException(status_code=500, detail=str(e))


# ============ ADMIN PRODUCT CATALOG ENDPOINTS ============

@api_router.post("/admin/products")
async def admin_create_product(request: CreateProductRequest, current_user: dict = Depends(get_current_user)):
    """Admin creates a new product in the central catalog (NEW STORE SYSTEM)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can create products")
    
    try:
        # Use product_catalog table (NEW SYSTEM) with correct field names
        product_data = {
            'id': str(uuid.uuid4()),
            'name': request.title,  # product_catalog uses 'name' field
            'description': request.description,
            'base_price': request.price,  # product_catalog uses 'base_price'
            'category': request.category,
            'images': request.images if hasattr(request, 'images') and request.images else [],
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase_admin.table('product_catalog').insert(product_data).execute()
        
        # Format response to match frontend expectations
        formatted_product = {
            'id': result.data[0].get('id'),
            'title': result.data[0].get('name'),
            'description': result.data[0].get('description'),
            'price': result.data[0].get('base_price'),
            'category': result.data[0].get('category'),
            'images': result.data[0].get('images', []),
            'created_at': result.data[0].get('created_at')
        }
        
        return {"success": True, "product": formatted_product}
    except Exception as e:
        logging.error(f"Admin create product error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.put("/admin/products/{product_id}")
async def admin_update_product(product_id: str, request: UpdateProductRequest, current_user: dict = Depends(get_current_user)):
    """Admin updates a product in the catalog (NEW STORE SYSTEM)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can update products")
    
    if current_user.get('banStatus') in ('banned', 'suspended'):
        raise HTTPException(status_code=403, detail="Your account is restricted. You cannot manage products.")
    
    try:
        # Use product_catalog table (NEW SYSTEM)
        product = supabase_admin.table('product_catalog').select('*').eq('id', product_id).execute()
        
        if not product.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        update_data = {}
        if request.title is not None:
            update_data['name'] = request.title  # product_catalog uses 'name' field
        if request.description is not None:
            update_data['description'] = request.description
        if request.price is not None:
            update_data['base_price'] = request.price  # product_catalog uses 'base_price'
        if request.images is not None:
            update_data['images'] = request.images
        if request.category is not None:
            update_data['category'] = request.category
        
        result = supabase_admin.table('product_catalog').update(update_data).eq('id', product_id).execute()
        
        # Format response to match frontend expectations
        formatted_product = {
            'id': result.data[0].get('id'),
            'title': result.data[0].get('name'),
            'description': result.data[0].get('description'),
            'price': result.data[0].get('base_price'),
            'category': result.data[0].get('category'),
            'images': result.data[0].get('images', []),
            'created_at': result.data[0].get('created_at'),
            'is_active': result.data[0].get('is_active', True)
        }
        
        return {"success": True, "product": formatted_product}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Admin update product error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.delete("/admin/products/{product_id}")
async def admin_delete_product(product_id: str, current_user: dict = Depends(get_current_user)):
    """Admin deletes a product from the catalog (NEW STORE SYSTEM)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can delete products")
    
    if current_user.get('banStatus') in ('banned', 'suspended') and current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Your account is restricted. You cannot manage products.")
    
    try:
        # Use product_catalog table (NEW SYSTEM)
        product = supabase_admin.table('product_catalog').select('*').eq('id', product_id).execute()
        
        if not product.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if product is used in any store_products (sellers added it to their stores)
        store_products = supabase_admin.table('store_products').select('id').eq('catalog_product_id', product_id).limit(1).execute()
        if store_products.data:
            # Instead of deleting, just deactivate the product
            supabase_admin.table('product_catalog').update({'is_active': False}).eq('id', product_id).execute()
            return {"success": True, "message": "Product deactivated (sellers are using it in their stores)"}
        
        # Delete product (no sellers using it, safe to delete)
        supabase_admin.table('product_catalog').delete().eq('id', product_id).execute()
        return {"success": True, "message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Admin delete product error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.put("/admin/products/{product_id}/toggle-active")
async def admin_toggle_product_active(product_id: str, current_user: dict = Depends(get_current_user)):
    """Admin toggles product active status"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can manage products")
    
    try:
        product = supabase_admin.table('products').select('*').eq('id', product_id).execute()
        
        if not product.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        current_status = product.data[0].get('is_active', True)
        new_status = not current_status
        
        result = supabase_admin.table('products').update({'is_active': new_status}).eq('id', product_id).execute()
        return {"success": True, "product": format_product_response(result.data[0]), "message": f"Product {'activated' if new_status else 'deactivated'}"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Admin toggle product error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============ SELLER CATALOG SELECTION ENDPOINTS ============

@api_router.get("/catalog/products")
async def get_catalog_products(category: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Sellers browse available products in the admin catalog"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can browse the catalog")
    
    try:
        query = supabase_admin.table('products').select('*')
        
        if category:
            query = query.eq('category', category)
        
        products = query.order('created_at', desc=True).execute()
        
        # Get seller's already selected products (seller_products table may not exist yet)
        selected_ids = set()
        try:
            seller_products = supabase_admin.table('seller_products').select('product_id').eq('seller_id', current_user['id']).eq('is_active', True).execute()
            selected_ids = set(sp['product_id'] for sp in seller_products.data) if seller_products.data else set()
        except:
            pass  # Table might not exist yet
        
        # Mark which products the seller has already selected
        catalog_products = []
        for p in products.data:
            product = format_product_response(p)
            product['isSelected'] = p['id'] in selected_ids
            catalog_products.append(product)
        
        return {"success": True, "products": catalog_products}
    except Exception as e:
        logging.error(f"Get catalog products error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/seller/products/{product_id}")
async def seller_add_product(product_id: str, current_user: dict = Depends(get_current_user)):
    """Seller adds a product from catalog to their store"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can add products to their store")
    
    if current_user['verificationStatus'] != 'verified':
        raise HTTPException(status_code=403, detail="Seller must be verified to add products")
    
    try:
        store_name = (current_user.get('storeName') or '').strip()
        if not store_name:
            seller_profile = supabase_admin.table('users').select('store_name').eq('id', current_user['id']).execute()
            if seller_profile.data:
                store_name = (seller_profile.data[0].get('store_name') or '').strip()
        if not store_name:
            raise HTTPException(status_code=400, detail="Store name is required to add products")
        
        # Check product exists
        product = supabase_admin.table('products').select('*').eq('id', product_id).execute()
        
        if not product.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if already added
        try:
            existing = supabase_admin.table('seller_products').select('id').eq('seller_id', current_user['id']).eq('product_id', product_id).execute()
            
            if existing.data:
                # Reactivate if was deactivated
                supabase_admin.table('seller_products').update({
                    'is_active': True,
                    'store_name': store_name,
                    'is_seller_product': True
                }).eq('seller_id', current_user['id']).eq('product_id', product_id).execute()
                return {"success": True, "message": "Product re-added to your store"}
        except Exception as e:
            if "seller_products" not in str(e):
                raise e
            # Table doesn't exist - will be created by first insert or needs manual setup
        
        # Add to seller's store
        seller_product_data = {
            'id': str(uuid.uuid4()),
            'seller_id': current_user['id'],
            'product_id': product_id,
            'is_active': True,
            'added_at': datetime.now(timezone.utc).isoformat(),
            'store_name': store_name,
            'is_seller_product': True
        }
        
        supabase_admin.table('seller_products').insert(seller_product_data).execute()
        return {"success": True, "message": "Product added to your store"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Seller add product error: {str(e)}")
        # If seller_products table doesn't exist, inform the user
        if "seller_products" in str(e):
            raise HTTPException(status_code=500, detail="Seller product system not yet configured. Please contact admin.")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.delete("/seller/products/{product_id}")
async def seller_remove_product(product_id: str, current_user: dict = Depends(get_current_user)):
    """Seller removes a product from their store"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can manage their store")
    
    try:
        # Deactivate instead of delete to preserve history
        result = supabase_admin.table('seller_products').update({'is_active': False}).eq('seller_id', current_user['id']).eq('product_id', product_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Product not found in your store")
        
        return {"success": True, "message": "Product removed from your store"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Seller remove product error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Legacy endpoint - redirect to admin
@api_router.post("/products")
async def create_product(request: CreateProductRequest, current_user: dict = Depends(get_current_user)):
    """Create new product - Admin only in new architecture"""
    if current_user['role'] == 'admin':
        return await admin_create_product(request, current_user)
    raise HTTPException(status_code=403, detail="Only admins can create products. Sellers can select products from the catalog.")


@api_router.put("/products/{product_id}")
async def update_product(product_id: str, request: UpdateProductRequest, current_user: dict = Depends(get_current_user)):
    """Update product - Admin only in new architecture"""
    if current_user['role'] == 'admin':
        return await admin_update_product(product_id, request, current_user)
    raise HTTPException(status_code=403, detail="Only admins can update products.")


@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, current_user: dict = Depends(get_current_user)):
    """Delete product - Admin only in new architecture"""
    if current_user['role'] == 'admin':
        return await admin_delete_product(product_id, current_user)
    raise HTTPException(status_code=403, detail="Only admins can delete products.")


@api_router.get("/admin/products")
async def get_all_products_admin(current_user: dict = Depends(get_current_user)):
    """Get all products from product_catalog for admin management"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Admin catalog - get all products from product_catalog (NEW STORE SYSTEM)
        products = supabase_admin.table('product_catalog').select('*').order('created_at', desc=True).execute()
        # Format response to match expected frontend format
        formatted_products = []
        for p in products.data:
            formatted_products.append({
                'id': p.get('id'),
                'title': p.get('name'),  # product_catalog uses 'name' field
                'description': p.get('description'),
                'price': p.get('base_price'),  # product_catalog uses 'base_price'
                'category': p.get('category'),
                'images': p.get('images', []),
                'created_at': p.get('created_at'),
                'is_active': p.get('is_active', True)
            })
        return {"success": True, "products": formatted_products}
    except Exception as e:
        logging.error(f"Get all products admin error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# NOTE: seed-catalog endpoint moved to STORE SYSTEM section (line ~3794)
# This endpoint now seeds to product_catalog table for the new store system


@api_router.delete("/admin/clear-legacy-products")
async def clear_legacy_products(current_user: dict = Depends(get_current_user)):
    """Clear all products from legacy 'products' table (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Check for products with orders
        all_products = supabase_admin.table('products').select('id').execute()
        products_with_orders = []
        
        for product in all_products.data:
            order_items = supabase_admin.table('order_items').select('id').eq('product_id', product['id']).limit(1).execute()
            if order_items.data:
                products_with_orders.append(product['id'])
        
        # Deactivate products with orders, delete others
        deactivated = 0
        deleted = 0
        
        for product in all_products.data:
            if product['id'] in products_with_orders:
                supabase_admin.table('products').update({'is_active': False}).eq('id', product['id']).execute()
                deactivated += 1
            else:
                supabase_admin.table('products').delete().eq('id', product['id']).execute()
                deleted += 1
        
        return {
            "success": True, 
            "message": f"Deleted {deleted} legacy products, deactivated {deactivated} products with orders"
        }
    except Exception as e:
        logging.error(f"Clear legacy products error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/products/{product_id}/upload-image")
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload product image (admin only in new architecture)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can upload product images")
    
    try:
        product = supabase_admin.table('products').select('*').eq('id', product_id).execute()
        
        if not product.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        current_images = product.data[0].get('images', [])
        if len(current_images) >= 10:
            raise HTTPException(status_code=400, detail="Maximum 10 images allowed")
        
        contents = await file.read()
        
        file_ext = file.filename.split('.')[-1]
        file_name = f"{product_id}/{str(uuid.uuid4())}.{file_ext}"
        
        supabase_admin.storage.from_('products').upload(file_name, contents, {
            'content-type': file.content_type
        })
        
        public_url = supabase_admin.storage.from_('products').get_public_url(file_name)
        
        updated_images = current_images + [public_url]
        supabase_admin.table('products').update({'images': updated_images}).eq('id', product_id).execute()
        
        return {"success": True, "imageUrl": public_url}
    except Exception as e:
        logging.error(f"Image upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


class RemoveImageRequest(BaseModel):
    imageUrl: str


@api_router.delete("/products/{product_id}/remove-image")
async def remove_product_image(
    product_id: str,
    request: RemoveImageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Remove product image (admin only in new architecture)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can remove product images")
    
    try:
        product = supabase_admin.table('products').select('*').eq('id', product_id).execute()
        
        if not product.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        current_images = product.data[0].get('images', [])
        
        if request.imageUrl not in current_images:
            raise HTTPException(status_code=404, detail="Image not found in product")
        
        # Remove from database
        updated_images = [img for img in current_images if img != request.imageUrl]
        supabase_admin.table('products').update({'images': updated_images}).eq('id', product_id).execute()
        
        # Try to delete from storage (extract file path from URL)
        try:
            if '/products/' in request.imageUrl:
                file_path = request.imageUrl.split('/products/')[-1].split('?')[0]
                supabase_admin.storage.from_('products').remove([file_path])
        except Exception as storage_error:
            logging.warning(f"Could not delete image from storage: {str(storage_error)}")
        
        return {"success": True, "message": "Image removed", "remainingImages": updated_images}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Image removal error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Order Routes
@api_router.post("/orders")
@limiter.limit("10/hour")
async def create_order(request: Request, req: CreateOrderRequest, current_user: dict = Depends(get_current_user)):
    """Create new order"""
    if current_user['role'] != 'buyer':
        raise HTTPException(status_code=403, detail="Only buyers can create orders")
    
    if current_user.get('banStatus') in ('banned', 'suspended'):
        raise HTTPException(status_code=403, detail="Your account is restricted. You cannot place orders.")
    
    # Validate shipping information is provided
    if not req.shippingAddress or not req.shippingName or not req.shippingPhone:
        raise HTTPException(status_code=400, detail="Shipping information is required")
    
    try:
        payment_method = 'WALLET' if req.useWallet else 'USDT_TRON'
        payment_status = 'paid' if req.useWallet else 'pending_payment'
        confirmed_by_admin = req.useWallet  # Auto-confirm wallet payments
        
        # If using wallet, check balance and deduct
        if req.useWallet:
            wallet = await get_or_create_buyer_wallet(current_user['id'])
            current_balance = float(wallet.get('balance', 0))
            
            if current_balance < req.totalAmount:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient wallet balance. Available: ${current_balance:.2f}, Required: ${req.totalAmount:.2f}"
                )
            
            # Deduct from wallet
            new_balance = current_balance - req.totalAmount
            supabase_admin.table('buyer_wallets').update({
                'balance': new_balance,
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }).eq('userId', current_user['id']).execute()
            
            # Create transaction record
            await create_wallet_transaction(
                user_id=current_user['id'],
                user_role='buyer',
                transaction_type='purchase',
                amount=-req.totalAmount,
                previous_balance=current_balance,
                new_balance=new_balance,
                description=f"Order payment: ${req.totalAmount:.2f}"
            )
        
        # Calculate deposit requirement (80% of total)
        deposit_required = req.totalAmount * 0.8
        
        # Set escrow status based on payment
        escrow_status = 'paid' if req.useWallet or payment_status == 'paid' else 'pending'
        
        order_data = {
            'id': str(uuid.uuid4()),
            'buyer_id': current_user['id'],
            'total_amount': req.totalAmount,
            'payment_method': payment_method,
            'payment_wallet': 'WALLET_BALANCE' if req.useWallet else ADMIN_CRYPTO_WALLET,
            'payment_status': payment_status,
            'confirmed_by_admin': confirmed_by_admin,
            'confirmed_at': datetime.now(timezone.utc).isoformat() if confirmed_by_admin else None,
            'shipping_address_id': req.shippingAddressId,
            'shipping_name': req.shippingName,
            'shipping_phone': req.shippingPhone,
            'shipping_address_snapshot': req.shippingAddress,
            'created_at': datetime.now(timezone.utc).isoformat(),
            # NEW: Escrow + Deposit fields
            'escrowStatus': escrow_status,
            'depositRequired': deposit_required
        }
        
        order_result = supabase_admin.table('orders').insert(order_data).execute()
        order_id = order_result.data[0]['id']
        
        order_items_list = []
        seller_amounts = {}  # Track amount per seller
        
        for item in req.items:
            # Handle both productId (camelCase) and product_id (snake_case)
            product_id = item.get('productId') or item.get('product_id')
            if not product_id:
                raise HTTPException(status_code=400, detail="Missing productId or product_id in order items")
            
            item_data = {
                'id': str(uuid.uuid4()),
                'order_id': order_id,
                'product_id': product_id,
                'quantity': item.get('quantity', 1),
                'price': item.get('price', 0)
            }
            supabase_admin.table('order_items').insert(item_data).execute()
            order_items_list.append(item_data)
            
            # Get seller for this product to create deposit requirement
            try:
                product_result = supabase_admin.table('store_products')\
                    .select('*, stores(seller_id)')\
                    .eq('id', product_id)\
                    .execute()
                
                if product_result.data:
                    store = product_result.data[0].get('stores')
                    if store:
                        seller_id = store.get('seller_id')
                        item_total = float(item.get('price', 0)) * int(item.get('quantity', 1))
                        if seller_id not in seller_amounts:
                            seller_amounts[seller_id] = 0
                        seller_amounts[seller_id] += item_total
            except Exception as e:
                logging.warning(f"Could not fetch seller for product {item['productId']}: {str(e)}")
        
        # If payment is confirmed (wallet payment), immediately move to awaiting_seller_deposit
        if req.useWallet or payment_status == 'paid':
            # Update order to awaiting_seller_deposit
            supabase_admin.table('orders').update({
                'escrow_status': 'awaiting_seller_deposit'
            }).eq('id', order_id).execute()
            
            # Record platform balance transaction (buyer payment received)
            try:
                platform_balance = supabase_admin.table('platform_balance')\
                    .select('*')\
                    .eq('id', '00000000-0000-0000-0000-000000000001')\
                    .execute()
                
                if platform_balance.data:
                    current_platform_balance = float(platform_balance.data[0].get('balance', 0))
                    new_platform_balance = current_platform_balance + req.totalAmount
                    
                    supabase_admin.table('platform_balance').update({
                        'balance': new_platform_balance,
                        'total_received': float(platform_balance.data[0].get('total_received', 0)) + req.totalAmount,
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    }).eq('id', '00000000-0000-0000-0000-000000000001').execute()
                    
                    # Record platform transaction
                    supabase_admin.table('platform_transactions').insert({
                        'transaction_type': 'buyer_payment',
                        'amount': req.totalAmount,
                        'order_id': order_id,
                        'user_id': current_user['id'],
                        'description': f'Buyer payment for order {order_id[:8]}',
                        'previous_balance': current_platform_balance,
                        'new_balance': new_platform_balance
                    }).execute()
            except Exception as e:
                logging.warning(f"Could not update platform wallet: {str(e)}")
            
            # Create deposit requirements for each seller
            for seller_id, seller_amount in seller_amounts.items():
                seller_deposit = seller_amount * 0.8  # 80% of seller's portion
                try:
                    supabase_admin.table('order_deposits').insert({
                        'order_id': order_id,
                        'seller_id': seller_id,
                        'required_amount': seller_deposit,
                        'deposited_amount': 0,
                        'is_deposit_complete': False
                    }).execute()
                except Exception as e:
                    logging.warning(f"Could not create deposit requirement for seller {seller_id}: {str(e)}")
        
        # If wallet payment, update transaction with order_id
        if req.useWallet:
            # Update the transaction with order_id
            transactions = supabase_admin.table('wallet_transactions').select('id').eq('userId', current_user['id']).order('createdAt', desc=True).limit(1).execute()
            if transactions.data:
                supabase_admin.table('wallet_transactions').update({
                    'orderId': order_id
                }).eq('id', transactions.data[0]['id']).execute()
        
        # Send email notifications (non-blocking)
        asyncio.create_task(send_order_notifications(order_data, order_items_list, "order_placed"))
        
        return {"success": True, "order": format_order_response(order_result.data[0])}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Create order error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/orders/my")
async def get_my_orders(current_user: dict = Depends(get_current_user)):
    """Get user's orders (updated for NEW store_products system)"""
    try:
        if current_user['role'] == 'buyer':
            # Buyer sees their own orders with product details from store_products
            orders = supabase_admin.table('orders')\
                .select('*, order_items(*, store_products(*, product_catalog(*)))')\
                .eq('buyer_id', current_user['id'])\
                .execute()
            
            # Format product info from store_products
            for order in orders.data:
                for item in order.get('order_items', []):
                    sp = item.get('store_products')
                    if sp:
                        catalog = sp.get('product_catalog', {})
                        item['products'] = {
                            'id': sp.get('id'),
                            'title': catalog.get('name'),
                            'description': catalog.get('description'),
                            'images': catalog.get('images', []),
                            'category': catalog.get('category'),
                            'price': sp.get('price')
                        }
            
        elif current_user['role'] == 'seller':
            # Seller sees orders containing their store products
            orders = supabase_admin.table('orders')\
                .select('*, order_items(*, store_products(*, product_catalog(*)))')\
                .execute()
            
            filtered_orders = []
            for order in orders.data:
                seller_items = []
                for item in order.get('order_items', []):
                    sp = item.get('store_products')
                    if sp and sp.get('seller_id') == current_user['id']:
                        catalog = sp.get('product_catalog', {})
                        item['products'] = {
                            'id': sp.get('id'),
                            'title': catalog.get('name'),
                            'description': catalog.get('description'),
                            'images': catalog.get('images', []),
                            'category': catalog.get('category'),
                            'price': sp.get('price')
                        }
                        seller_items.append(item)
                
                if seller_items:
                    order['order_items'] = seller_items
                    
                    # Fetch deposit status for this order and seller
                    try:
                        deposit_result = supabase_admin.table('order_deposits')\
                            .select('*')\
                            .eq('order_id', order['id'])\
                            .eq('seller_id', current_user['id'])\
                            .execute()
                        
                        if deposit_result.data:
                            deposit = deposit_result.data[0]
                            order['depositInfo'] = {
                                'depositStatus': deposit.get('deposit_status'),
                                'depositMethod': deposit.get('deposit_method'),
                                'transactionHash': deposit.get('transaction_hash'),
                                'submittedAt': deposit.get('submitted_at'),
                                'isComplete': deposit.get('is_deposit_complete')
                            }
                    except Exception as e:
                        logging.warning(f"Could not fetch deposit for order {order['id']}: {str(e)}")
                        order['depositInfo'] = None
                    
                    filtered_orders.append(order)
            
            return {"success": True, "orders": [format_order_response(o) for o in filtered_orders]}
            
        elif current_user['role'] == 'admin':
            # Admin sees all orders
            orders = supabase_admin.table('orders')\
                .select('*, order_items(*, store_products(*, product_catalog(*))), users!buyer_id(name, email)')\
                .execute()
            
            # Format product info
            for order in orders.data:
                for item in order.get('order_items', []):
                    sp = item.get('store_products')
                    if sp:
                        catalog = sp.get('product_catalog', {})
                        item['products'] = {
                            'id': sp.get('id'),
                            'title': catalog.get('name'),
                            'description': catalog.get('description'),
                            'images': catalog.get('images', []),
                            'category': catalog.get('category'),
                            'price': sp.get('price')
                        }
        else:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        return {"success": True, "orders": [format_order_response(o) for o in orders.data]}
    except Exception as e:
        logging.error(f"Get orders error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/seller/earnings")
async def get_seller_earnings(current_user: dict = Depends(get_current_user)):
    """Get seller earnings, balances, and payout summaries."""
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can view earnings")

    try:
        # 1) Fetch ONLY COMPLETED orders (not just paid)
        # Earnings should only be counted when order is completed
        orders_result = (
            supabase_admin.table("orders")
            .select("*, order_items(*, store_products!inner(seller_id))")
            .eq("payment_status", "completed")  # Changed: ONLY completed orders
            .execute()
        )

        total_earnings = 0.0
        for order in orders_result.data or []:
            for item in order.get("order_items", []):
                store_product = item.get("store_products") or {}
                # Check if this product belongs to the current seller
                if store_product.get("seller_id") == current_user["id"]:
                    total_earnings += float(item.get("price", 0)) * int(item.get("quantity", 0))

        # 2) Fetch payout requests for this seller
        payouts_result = (
            supabase_admin.table("payout_requests")
            .select("*")
            .eq("sellerId", current_user["id"])
            .execute()
        )

        total_withdrawn = 0.0
        pending_withdrawals = 0.0
        completed_withdrawals = 0.0

        payout_history = []
        for p in payouts_result.data or []:
            amount = float(p.get("requestedAmount") or p.get("requested_amount", 0))
            status = p.get("status")
            if status in ("approved", "paid"):
                total_withdrawn += amount
                completed_withdrawals += amount if status == "paid" else 0.0
            if status == "pending":
                pending_withdrawals += amount
            payout_history.append(format_payout_request_response(p))

        available_balance = max(total_earnings - total_withdrawn, 0.0)

        return {
            "success": True,
            "earnings": {
                "totalEarnings": round(total_earnings, 2),
                "availableBalance": round(available_balance, 2),
                "pendingWithdrawals": round(pending_withdrawals, 2),
                "completedWithdrawals": round(completed_withdrawals, 2),
                "payoutRequests": payout_history,
            },
        }
    except Exception as e:
        logging.error(f"Get seller earnings error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/seller/payout-requests")
async def create_payout_request(req: CreatePayoutRequest, current_user: dict = Depends(get_current_user)):
    """Seller creates a payout request from available balance."""
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can request payouts")

    if req.requestedAmount <= 0:
        raise HTTPException(status_code=400, detail="Requested amount must be greater than zero")
    
    # Validate wallet address is provided
    if not req.payoutWallet or not req.payoutWallet.strip():
        raise HTTPException(status_code=400, detail="USDT TRC20 wallet address is required")
    
    # Basic TRC20 wallet validation (starts with 'T' and is 34 characters)
    wallet_address = req.payoutWallet.strip()
    if not wallet_address.startswith('T') or len(wallet_address) != 34:
        raise HTTPException(status_code=400, detail="Invalid USDT TRC20 wallet address. Must start with 'T' and be 34 characters long")

    try:
        # Reuse earnings calculation to determine available balance
        earnings_response = await get_seller_earnings(current_user)
        available_balance = earnings_response["earnings"]["availableBalance"]

        if req.requestedAmount > available_balance:
            raise HTTPException(status_code=400, detail="Requested amount exceeds available balance")

        data = {
            "sellerId": current_user["id"],
            "requestedAmount": req.requestedAmount,
            "status": "pending",
            "payoutWallet": wallet_address,
            "requestDate": datetime.now(timezone.utc).isoformat(),
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }

        result = supabase_admin.table("payout_requests").insert(data).execute()
        created = result.data[0] if result.data else data

        return {"success": True, "payoutRequest": format_payout_request_response(created)}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Create payout request error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/seller/payout-requests")
async def get_seller_payout_requests(current_user: dict = Depends(get_current_user)):
    """Seller views their payout request history"""
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can view payout requests")

    try:
        # Get all payout requests for this seller
        payouts_result = (
            supabase_admin.table("payout_requests")
            .select("*")
            .eq("sellerId", current_user["id"])
            .order("requestDate", desc=True)
            .execute()
        )

        payouts = [format_payout_request_response(p) for p in (payouts_result.data or [])]

        return {"success": True, "payoutRequests": payouts}
    except Exception as e:
        logging.error(f"Get payout requests error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/seller/wallet/recharge")
async def request_seller_wallet_recharge(req: WalletRechargeRequest, current_user: dict = Depends(get_current_user)):
    """Seller requests wallet recharge with USDT TRC20 (requires admin approval)"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can recharge wallet")
    
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")
    
    # USDT TRC20 wallet address for payments
    ADMIN_USDT_WALLET = "TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU"
    
    try:
        recharge_data = {
            'id': str(uuid.uuid4()),
            'sellerId': current_user['id'],
            'amount': req.amount,
            'status': 'pending',
            'paymentMethod': 'USDT_TRON',
            'paymentWallet': ADMIN_USDT_WALLET,
            'transactionHash': req.paymentWallet,  # User provides their transaction hash
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'updatedAt': datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase_admin.table('seller_wallet_recharge_requests').insert(recharge_data).execute()
        
        return {
            "success": True,
            "message": "Recharge request submitted. Awaiting admin approval.",
            "rechargeRequest": result.data[0] if result.data else recharge_data,
            "paymentWallet": ADMIN_USDT_WALLET
        }
    except Exception as e:
        logging.error(f"Seller wallet recharge error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/seller/wallet/recharge-requests")
async def get_seller_recharge_requests(current_user: dict = Depends(get_current_user)):
    """Get seller's wallet recharge request history"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can view recharge requests")
    
    try:
        result = supabase_admin.table('seller_wallet_recharge_requests').select('*').eq('sellerId', current_user['id']).order('createdAt', desc=True).execute()
        
        return {
            "success": True,
            "rechargeRequests": result.data or []
        }
    except Exception as e:
        logging.error(f"Get seller recharge requests error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/seller/wallet/balance")
async def get_seller_wallet_balance(current_user: dict = Depends(get_current_user)):
    """Get seller's wallet balance (from recharges) and total summary"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can view wallet balance")
    
    try:
        # Get or create seller wallet
        wallet = await get_or_create_seller_wallet(current_user['id'])
        wallet_balance = float(wallet.get('balance', 0))
        wallet_total_recharged = float(wallet.get('totalEarnings') or wallet.get('total_earnings', 0))
        
        # Get pending recharge requests
        pending_result = (
            supabase_admin.table('seller_wallet_recharge_requests')
            .select('amount')
            .eq('sellerId', current_user['id'])
            .eq('status', 'pending')
            .execute()
        )
        pending_recharges = sum(float(r.get('amount', 0)) for r in (pending_result.data or []))
        
        # Get approved recharge requests (for history)
        approved_result = (
            supabase_admin.table('seller_wallet_recharge_requests')
            .select('amount')
            .eq('sellerId', current_user['id'])
            .eq('status', 'approved')
            .execute()
        )
        total_approved_recharges = sum(float(r.get('amount', 0)) for r in (approved_result.data or []))
        
        return {
            "success": True,
            "wallet": {
                "balance": round(wallet_balance, 2),
                "totalRecharged": round(wallet_total_recharged, 2),
                "pendingRecharges": round(pending_recharges, 2),
                "approvedRecharges": round(total_approved_recharges, 2),
                "updatedAt": wallet.get('updatedAt') or wallet.get('updated_at')
            }
        }
    except Exception as e:
        logging.error(f"Get seller wallet balance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/admin/seller-wallet-recharge-requests")
async def admin_get_seller_recharge_requests(current_user: dict = Depends(get_current_user)):
    """Admin can view all seller wallet recharge requests"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Fetch recharge requests without join (no FK relationship exists)
        result = (
            supabase_admin.table('seller_wallet_recharge_requests')
            .select('*')
            .order('createdAt', desc=True)
            .execute()
        )
        
        requests = []
        for r in (result.data or []):
            # Fetch seller info separately
            seller_id = r.get('sellerId')
            seller_name = None
            seller_email = None
            
            if seller_id:
                try:
                    user_result = supabase_admin.table('users').select('name, email').eq('id', seller_id).execute()
                    if user_result.data:
                        seller_name = user_result.data[0].get('name')
                        seller_email = user_result.data[0].get('email')
                except Exception as user_err:
                    logging.warning(f"Could not fetch seller info for {seller_id}: {str(user_err)}")
            
            payload = {
                "id": r.get('id'),
                "sellerId": seller_id,
                "sellerName": seller_name,
                "sellerEmail": seller_email,
                "amount": float(r.get('amount', 0)),
                "status": r.get('status'),
                "paymentMethod": r.get('paymentMethod'),
                "paymentWallet": r.get('paymentWallet'),
                "transactionHash": r.get('transactionHash'),
                "adminNote": r.get('adminNote'),
                "createdAt": r.get('createdAt'),
                "updatedAt": r.get('updatedAt')
            }
            requests.append(payload)
        
        return {"success": True, "requests": requests}
    except Exception as e:
        logging.error(f"Admin get seller recharge requests error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/seller-wallet-recharge-requests/{request_id}/status")
async def admin_update_seller_recharge_status(
    request_id: str,
    req: UpdateRechargeStatusRequest,
    current_user: dict = Depends(get_current_user)
):
    """Admin approves or rejects seller wallet recharge request"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if req.status not in ('approved', 'rejected'):
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'approved' or 'rejected'")
    
    try:
        # Get the recharge request
        recharge_result = supabase_admin.table('seller_wallet_recharge_requests').select('*').eq('id', request_id).execute()
        
        if not recharge_result.data:
            raise HTTPException(status_code=404, detail="Recharge request not found")
        
        recharge = recharge_result.data[0]
        seller_id = recharge['sellerId']
        amount = float(recharge['amount'])
        
        # Update the recharge request status
        update_data = {
            'status': req.status,
            'adminNote': req.adminNote,
            'updatedAt': datetime.now(timezone.utc).isoformat()
        }
        
        supabase_admin.table('seller_wallet_recharge_requests').update(update_data).eq('id', request_id).execute()
        
        # If approved, credit the seller's wallet
        if req.status == 'approved':
            # Get or create seller wallet
            wallet_result = supabase_admin.table('seller_wallets').select('*').eq('userId', seller_id).execute()
            
            if wallet_result.data:
                # Update existing wallet
                current_balance = float(wallet_result.data[0].get('balance', 0))
                new_balance = current_balance + amount
                
                supabase_admin.table('seller_wallets').update({
                    'balance': new_balance,
                    'updatedAt': datetime.now(timezone.utc).isoformat()
                }).eq('userId', seller_id).execute()
            else:
                # Create new wallet
                supabase_admin.table('seller_wallets').insert({
                    'id': str(uuid.uuid4()),
                    'userId': seller_id,
                    'balance': amount,
                    'totalEarnings': 0,
                    'createdAt': datetime.now(timezone.utc).isoformat(),
                    'updatedAt': datetime.now(timezone.utc).isoformat()
                }).execute()
            
            # Create wallet transaction record
            await create_wallet_transaction(
                user_id=seller_id,
                user_role='seller',
                transaction_type='recharge',
                amount=amount,
                previous_balance=current_balance if wallet_result.data else 0,
                new_balance=(current_balance if wallet_result.data else 0) + amount,
                description=f"Wallet recharge approved: ${amount:.2f} (USDT TRC20)"
            )
        
        return {
            "success": True,
            "message": f"Recharge request {req.status}",
            "status": req.status
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Admin update seller recharge status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/seller/payout-requests")
async def get_seller_payout_requests(current_user: dict = Depends(get_current_user)):
    """Get all payout requests for the current seller."""
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can view payout requests")

    try:
        result = (
            supabase_admin.table("payout_requests")
            .select("*")
            .eq("sellerId", current_user["id"])
            .order("requestDate", desc=True)
            .execute()
        )
        return {
            "success": True,
            "payoutRequests": [format_payout_request_response(p) for p in result.data or []],
        }
    except Exception as e:
        logging.error(f"Get seller payout requests error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Wallet Routes - Buyer
@api_router.get("/wallet/balance")
async def get_wallet_balance(current_user: dict = Depends(get_current_user)):
    """Get buyer wallet balance"""
    if current_user['role'] != 'buyer':
        raise HTTPException(status_code=403, detail="Only buyers can view wallet balance")
    
    try:
        wallet = await get_or_create_buyer_wallet(current_user['id'])
        return {
            "success": True,
            "balance": float(wallet.get('balance', 0)),
            "wallet": {
                "id": wallet.get('id'),
                "userId": wallet.get('userId') or wallet.get('user_id'),
                "balance": float(wallet.get('balance', 0)),
                "createdAt": wallet.get('createdAt') or wallet.get('created_at'),
                "updatedAt": wallet.get('updatedAt') or wallet.get('updated_at')
            }
        }
    except Exception as e:
        logging.error(f"Get wallet balance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/wallet/recharge")
async def request_wallet_recharge(req: WalletRechargeRequest, current_user: dict = Depends(get_current_user)):
    """Request wallet recharge (requires admin approval)"""
    if current_user['role'] != 'buyer':
        raise HTTPException(status_code=403, detail="Only buyers can recharge wallet")
    
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")
    
    try:
        recharge_data = {
            'id': str(uuid.uuid4()),
            'buyerId': current_user['id'],
            'amount': req.amount,
            'status': 'pending',
            'paymentMethod': req.paymentMethod or 'USDT_TRON',
            'paymentWallet': req.paymentWallet or ADMIN_CRYPTO_WALLET,
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'updatedAt': datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase_admin.table('wallet_recharge_requests').insert(recharge_data).execute()
        
        return {
            "success": True,
            "message": "Recharge request submitted. Awaiting admin approval.",
            "rechargeRequest": format_wallet_recharge_request_response(result.data[0] if result.data else recharge_data)
        }
    except Exception as e:
        logging.error(f"Request wallet recharge error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/wallet/transactions")
async def get_wallet_transactions(current_user: dict = Depends(get_current_user)):
    """Get wallet transaction history"""
    if current_user['role'] not in ['buyer', 'seller']:
        raise HTTPException(status_code=403, detail="Only buyers and sellers can view wallet transactions")
    
    try:
        result = (
            supabase_admin.table('wallet_transactions')
            .select('*')
            .eq('userId', current_user['id'])
            .order('createdAt', desc=True)
            .limit(100)
            .execute()
        )
        
        return {
            "success": True,
            "transactions": [format_wallet_transaction_response(t) for t in (result.data or [])]
        }
    except Exception as e:
        logging.error(f"Get wallet transactions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/wallet/recharge-requests")
async def get_wallet_recharge_requests(current_user: dict = Depends(get_current_user)):
    """Get buyer's recharge request history"""
    if current_user['role'] != 'buyer':
        raise HTTPException(status_code=403, detail="Only buyers can view recharge requests")
    
    try:
        result = (
            supabase_admin.table('wallet_recharge_requests')
            .select('*')
            .eq('buyerId', current_user['id'])
            .order('createdAt', desc=True)
            .execute()
        )
        
        return {
            "success": True,
            "rechargeRequests": [format_wallet_recharge_request_response(r) for r in (result.data or [])]
        }
    except Exception as e:
        logging.error(f"Get recharge requests error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, request: UpdateOrderStatusRequest, current_user: dict = Depends(get_current_user)):
    """Update order status (admin only). When order is completed, update seller wallets."""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can update order status")
    
    try:
        update_data = {
            'payment_status': request.status,
            'order_status': request.status  # Also update order_status for Order Center
        }
        
        if request.status == 'paid':
            update_data['confirmed_by_admin'] = True
            update_data['confirmed_at'] = datetime.now(timezone.utc).isoformat()
            # When paid, set order_status to 'to_be_shipped' so seller can ship
            update_data['order_status'] = 'to_be_shipped'
            # NEW: Also set escrow status to awaiting_seller_deposit
            update_data['escrow_status'] = 'awaiting_seller_deposit'
            
            # NEW: Record payment to platform wallet and create deposit requirements
            try:
                # Get order details first
                order_query = supabase_admin.table('orders')\
                    .select('*, order_items(*, store_products(stores(seller_id)))')\
                    .eq('id', order_id)\
                    .execute()
                
                if order_query.data:
                    order = order_query.data[0]
                    total_amount = float(order.get('total_amount', 0))
                    
                    # Update platform balance
                    platform_balance = supabase_admin.table('platform_balance')\
                        .select('*')\
                        .eq('id', '00000000-0000-0000-0000-000000000001')\
                        .execute()
                    
                    if platform_balance.data:
                        current_balance = float(platform_balance.data[0].get('balance', 0))
                        new_balance = current_balance + total_amount
                        
                        supabase_admin.table('platform_balance').update({
                            'balance': new_balance,
                            'total_received': float(platform_balance.data[0].get('total_received', 0)) + total_amount,
                            'updated_at': datetime.now(timezone.utc).isoformat()
                        }).eq('id', '00000000-0000-0000-0000-000000000001').execute()
                        
                        # Record transaction
                        supabase_admin.table('platform_transactions').insert({
                            'transaction_type': 'buyer_payment',
                            'amount': total_amount,
                            'order_id': order_id,
                            'user_id': order.get('buyer_id'),
                            'description': f'Admin confirmed payment for order {order_id[:8]}',
                            'previous_balance': current_balance,
                            'new_balance': new_balance
                        }).execute()
                    
                    # Create deposit requirements per seller
                    seller_amounts = {}
                    for item in order.get('order_items', []):
                        store_product = item.get('store_products')
                        if store_product:
                            store = store_product.get('stores')
                            if store:
                                seller_id = store.get('seller_id')
                                item_total = float(item.get('price', 0)) * int(item.get('quantity', 1))
                                if seller_id not in seller_amounts:
                                    seller_amounts[seller_id] = 0
                                seller_amounts[seller_id] += item_total
                    
                    for seller_id, seller_amount in seller_amounts.items():
                        seller_deposit = seller_amount * 0.8
                        try:
                            supabase_admin.table('order_deposits').insert({
                                'order_id': order_id,
                                'seller_id': seller_id,
                                'required_amount': seller_deposit,
                                'deposited_amount': 0,
                                'is_deposit_complete': False
                            }).execute()
                        except Exception as e:
                            logging.warning(f"Deposit requirement may already exist for seller {seller_id}: {str(e)}")
            except Exception as e:
                logging.error(f"Error creating deposit requirements: {str(e)}")
        elif request.status == 'completed':
            # When completed, set both statuses to completed
            update_data['order_status'] = 'completed'
            update_data['payment_status'] = 'completed'
        
        result = supabase_admin.table('orders').update(update_data).eq('id', order_id).execute()
        
        # When order is completed, update seller wallets with earnings
        if result.data and request.status == 'completed':
            order_data = result.data[0]
            # Fetch order items with store_products (NEW system)
            order_items_result = supabase_admin.table('order_items').select('*, store_products!inner(seller_id)').eq('order_id', order_id).execute()
            
            # Group earnings by seller
            seller_earnings = {}
            for item in (order_items_result.data or []):
                store_product = item.get('store_products', {})
                seller_id = store_product.get('seller_id')
                if seller_id:
                    earnings = float(item.get('price', 0)) * int(item.get('quantity', 0))
                    seller_earnings[seller_id] = seller_earnings.get(seller_id, 0) + earnings
            
            # Update each seller's wallet
            for seller_id, earnings_amount in seller_earnings.items():
                seller_wallet = await get_or_create_seller_wallet(seller_id)
                current_balance = float(seller_wallet.get('balance', 0))
                # Handle depositBalance - may not exist if migration not run
                current_deposit_balance = float(seller_wallet.get('depositBalance') or seller_wallet.get('deposit_balance', 0))
                current_total_earnings = float(seller_wallet.get('totalEarnings') or seller_wallet.get('total_earnings', 0))
                
                # Get deposit for this order to return it
                deposit_result = supabase_admin.table('order_deposits')\
                    .select('*')\
                    .eq('order_id', order_id)\
                    .eq('seller_id', seller_id)\
                    .execute()
                
                deposit_to_return = 0.0
                if deposit_result.data:
                    deposit_to_return = float(deposit_result.data[0].get('deposited_amount', 0))
                
                # IMPORTANT: Balance should ONLY change through approved recharge requests
                # Do NOT add earnings to balance - only track in totalEarnings
                # Do NOT modify balance for deposit returns
                new_deposit_balance = max(current_deposit_balance - deposit_to_return, 0)
                new_total_earnings = current_total_earnings + earnings_amount
                
                # Prepare update data - DO NOT UPDATE BALANCE, only totalEarnings and depositBalance
                wallet_update = {
                    'totalEarnings': new_total_earnings,
                    'updatedAt': datetime.now(timezone.utc).isoformat()
                }
                
                # Only update depositBalance if column exists (migration was run)
                if 'depositBalance' in seller_wallet or 'deposit_balance' in seller_wallet:
                    wallet_update['depositBalance'] = new_deposit_balance
                
                supabase_admin.table('seller_wallets').update(wallet_update).eq('userId', seller_id).execute()
                
                # Create transaction record for earnings tracking (not balance change)
                # NOTE: This records the earning but does NOT change wallet balance
                await create_wallet_transaction(
                    user_id=seller_id,
                    user_role='seller',
                    transaction_type='earning',
                    amount=earnings_amount,
                    previous_balance=current_balance,
                    new_balance=current_balance,  # Balance unchanged - only recharge requests change balance
                    order_id=order_id,
                    description=f"Earnings from order: ${earnings_amount:.2f} (Deposit: ${deposit_to_return:.2f} returned) [Balance unchanged - only recharge requests modify balance]"
                )
        
        # Send email notifications based on status change
        if result.data:
            order_data = result.data[0]
            if request.status == 'paid':
                asyncio.create_task(send_order_notifications(order_data, [], "payment_confirmed"))
            elif request.status == 'completed':
                asyncio.create_task(send_order_notifications(order_data, [], "order_completed"))
        
        return {"success": True, "order": format_order_response(result.data[0])}
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
        if current_user['role'] == 'seller':
            if not merchantInviteCode:
                raise HTTPException(status_code=400, detail="Merchant invite code required for sellers")
            
            code_check = supabase_admin.table('merchant_invite_codes').select('*').eq('code', merchantInviteCode).eq('is_used', False).execute()
            
            if not code_check.data:
                raise HTTPException(status_code=400, detail="Invalid or already used invite code")
        
        contents = await file.read()
        
        file_ext = file.filename.split('.')[-1]
        file_name = f"{current_user['id']}/{str(uuid.uuid4())}.{file_ext}"
        
        supabase_admin.storage.from_('documents').upload(file_name, contents, {
            'content-type': file.content_type
        })
        
        public_url = supabase_admin.storage.from_('documents').get_public_url(file_name)
        
        doc_data = {
            'id': str(uuid.uuid4()),
            'user_id': current_user['id'],
            'document_type': documentType,
            'document_url': public_url,
            'status': 'pending',
            'merchant_invite_code': merchantInviteCode if current_user['role'] == 'seller' else None,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase_admin.table('verification_documents').insert(doc_data).execute()
        
        supabase_admin.table('users').update({'verification_status': 'pending'}).eq('id', current_user['id']).execute()
        
        if current_user['role'] == 'seller' and merchantInviteCode:
            supabase_admin.table('merchant_invite_codes').update({
                'is_used': True,
                'used_by_user_id': current_user['id'],
                'used_at': datetime.now(timezone.utc).isoformat()
            }).eq('code', merchantInviteCode).execute()
        
        return {"success": True, "document": format_verification_doc_response(result.data[0])}
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/verification/documents")
async def get_verification_documents(current_user: dict = Depends(get_current_user)):
    """Get verification documents with SIGNED URLs for private access"""
    try:
        if current_user['role'] == 'admin':
            docs = supabase_admin.table('verification_documents').select('*, users(name, email, role)').eq('status', 'pending').execute()
        else:
            docs = supabase_admin.table('verification_documents').select('*').eq('user_id', current_user['id']).execute()
        
        formatted_docs = []
        for doc in docs.data:
            formatted_doc = format_verification_doc_response(doc)
            if formatted_doc.get('documentUrl'):
                if '/documents/' in formatted_doc['documentUrl']:
                    file_path = formatted_doc['documentUrl'].split('/documents/')[-1]
                    signed_url = get_signed_document_url(file_path, expires_in=3600)
                    if signed_url:
                        formatted_doc['documentUrl'] = signed_url
                    else:
                        logging.warning(f"Failed to generate signed URL for document {formatted_doc['id']}")
            formatted_docs.append(formatted_doc)
        
        return {"success": True, "documents": formatted_docs}
    except Exception as e:
        logging.error(f"Failed to fetch verification documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/verification/documents/{doc_id}/review")
async def review_verification(doc_id: str, request: ReviewVerificationRequest, current_user: dict = Depends(get_current_user)):
    """Review verification document (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can review documents")
    
    try:
        doc = supabase_admin.table('verification_documents').select('*').eq('id', doc_id).execute()
        
        if not doc.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        update_data = {
            'status': request.status,
            'reviewed_at': datetime.now(timezone.utc).isoformat()
        }
        
        if request.rejectionReason:
            update_data['rejection_reason'] = request.rejectionReason
        
        supabase_admin.table('verification_documents').update(update_data).eq('id', doc_id).execute()
        
        user_id = doc.data[0]['user_id']
        supabase_admin.table('users').update({'verification_status': request.status}).eq('id', user_id).execute()
        
        # Send verification email to user
        asyncio.create_task(send_verification_email(
            user_id, 
            request.status, 
            request.rejectionReason
        ))
        
        return {"success": True, "message": "Review completed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Store name change routes
@api_router.post("/seller/store-name-change")
async def request_store_name_change(request: StoreNameChangeRequest, current_user: dict = Depends(get_current_user)):
    """Seller requests a store name change. Admin must approve."""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can request store name changes")

    new_name = (request.newStoreName or "").strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="New store name is required")
    if len(new_name) < 2:
        raise HTTPException(status_code=400, detail="Store name must be at least 2 characters")
    if len(new_name) > 100:
        raise HTTPException(status_code=400, detail="Store name must be less than 100 characters")

    current_store = current_user.get('storeName') or ''
    if current_store and current_store.lower() == new_name.lower():
        raise HTTPException(status_code=400, detail="New store name must be different from current store name")

    try:
        # Ensure requested name is not already used by another seller
        existing = supabase_admin.table('users').select('id').eq('store_name', new_name).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Store name already taken. Please choose a different name.")

        # Prevent multiple pending requests per seller
        pending = supabase_admin.table('store_name_change_requests').select('id') \
            .eq('seller_id', current_user['id']).eq('status', 'pending').execute()
        if pending.data:
            raise HTTPException(status_code=400, detail="You already have a pending store name change request")

        data = {
            'seller_id': current_user['id'],
            'old_store_name': current_store,
            'new_store_name': new_name,
            'status': 'pending',
        }
        result = supabase_admin.table('store_name_change_requests').insert(data).execute()
        created = result.data[0] if result.data else data

        return {
            "success": True,
            "request": {
                "id": created.get('id'),
                "oldStoreName": created.get('old_store_name'),
                "newStoreName": created.get('new_store_name'),
                "status": created.get('status'),
                "adminNote": created.get('admin_note'),
                "createdAt": created.get('created_at'),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/seller/store-name-change")
async def get_store_name_change_request(current_user: dict = Depends(get_current_user)):
    """Get latest store name change request for current seller."""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can view store name change requests")

    try:
        result = supabase_admin.table('store_name_change_requests') \
            .select('*').eq('seller_id', current_user['id']) \
            .order('created_at', desc=True).limit(1).execute()

        if not result.data:
            return {"success": True, "request": None}

        req = result.data[0]
        return {
            "success": True,
            "request": {
                "id": req.get('id'),
                "oldStoreName": req.get('old_store_name'),
                "newStoreName": req.get('new_store_name'),
                "status": req.get('status'),
                "adminNote": req.get('admin_note'),
                "createdAt": req.get('created_at'),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Admin Routes
@api_router.get("/admin/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)."""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        # Fetch all users without pagination
        result = supabase_admin.table('users').select('*').execute()
        users_data = result.data or []

        return {
            "success": True,
            "users": [format_user_response(u) for u in users_data],
        }
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
            'is_used': False,
            'created_by_admin': current_user['id'],
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase_admin.table('merchant_invite_codes').insert(code_data).execute()
        return {"success": True, "inviteCode": format_invite_code_response(result.data[0])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/admin/invite-codes")
async def get_invite_codes(current_user: dict = Depends(get_current_user)):
    """Get all invite codes (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        codes = supabase_admin.table('merchant_invite_codes').select('*').execute()
        return {"success": True, "codes": [format_invite_code_response(c) for c in codes.data]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/admin/payout-requests")
async def admin_get_payout_requests(current_user: dict = Depends(get_current_user)):
    """Admin can view all payout requests from sellers."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        result = (
            supabase_admin.table("payout_requests")
            .select("*, users:sellerId(name, email, store_name)")
            .order("requestDate", desc=True)
            .execute()
        )

        requests = []
        for r in result.data or []:
            seller = r.get("users") or {}
            payload = format_payout_request_response(r)
            payload["sellerName"] = seller.get("name")
            payload["sellerEmail"] = seller.get("email")
            payload["sellerStoreName"] = seller.get("store_name")
            requests.append(payload)

        return {"success": True, "requests": requests}
    except Exception as e:
        logging.error(f"Admin get payout requests error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/payout-requests/{request_id}/status")
async def admin_update_payout_status(
    request_id: str,
    req: UpdatePayoutStatusRequest,
    current_user: dict = Depends(get_current_user),
):
    """Admin approves, rejects, or marks payout request as paid (manual payment)."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    if req.status not in ("approved", "rejected", "paid"):
        raise HTTPException(status_code=400, detail="Invalid payout status")

    try:
        # Ensure request exists
        existing = (
            supabase_admin.table("payout_requests")
            .select("*")
            .eq("id", request_id)
            .single()
            .execute()
        )
        payout = existing.data
        if not payout:
            raise HTTPException(status_code=404, detail="Payout request not found")

        update_data = {
            "status": req.status,
            "adminId": current_user["id"],
            "adminActionTimestamp": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }
        if req.adminNote is not None:
            update_data["adminNote"] = req.adminNote

        result = (
            supabase_admin.table("payout_requests")
            .update(update_data)
            .eq("id", request_id)
            .execute()
        )
        updated = result.data[0] if result.data else {**payout, **update_data}

        return {"success": True, "payoutRequest": format_payout_request_response(updated)}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Admin update payout status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Admin Wallet Management Routes
@api_router.get("/admin/wallets")
async def admin_get_all_wallets(current_user: dict = Depends(get_current_user)):
    """Admin can view all buyer and seller wallets"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get all buyer wallets
        buyer_wallets_result = supabase_admin.table('buyer_wallets').select('*, users:userId(name, email)').execute()
        buyer_wallets = []
        for wallet in (buyer_wallets_result.data or []):
            user = wallet.get('users') or {}
            buyer_wallets.append({
                'id': wallet.get('id'),
                'userId': wallet.get('userId') or wallet.get('user_id'),
                'userName': user.get('name'),
                'userEmail': user.get('email'),
                'balance': float(wallet.get('balance', 0)),
                'role': 'buyer',
                'createdAt': wallet.get('createdAt') or wallet.get('created_at'),
                'updatedAt': wallet.get('updatedAt') or wallet.get('updated_at')
            })
        
        # Get all seller wallets
        seller_wallets_result = supabase_admin.table('seller_wallets').select('*, users:userId(name, email, store_name)').execute()
        seller_wallets = []
        for wallet in (seller_wallets_result.data or []):
            user = wallet.get('users') or {}
            seller_wallets.append({
                'id': wallet.get('id'),
                'userId': wallet.get('userId') or wallet.get('user_id'),
                'userName': user.get('name'),
                'userEmail': user.get('email'),
                'storeName': user.get('store_name'),
                'balance': float(wallet.get('balance', 0)),
                'totalEarnings': float(wallet.get('totalEarnings') or wallet.get('total_earnings', 0)),
                'role': 'seller',
                'createdAt': wallet.get('createdAt') or wallet.get('created_at'),
                'updatedAt': wallet.get('updatedAt') or wallet.get('updated_at')
            })
        
        return {
            "success": True,
            "buyerWallets": buyer_wallets,
            "sellerWallets": seller_wallets
        }
    except Exception as e:
        logging.error(f"Admin get wallets error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/admin/wallet-recharge-requests")
async def admin_get_recharge_requests(current_user: dict = Depends(get_current_user)):
    """Admin can view all wallet recharge requests"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = (
            supabase_admin.table('wallet_recharge_requests')
            .select('*, users:buyerId(name, email)')
            .order('createdAt', desc=True)
            .execute()
        )
        
        requests = []
        for r in (result.data or []):
            buyer = r.get('users') or {}
            payload = format_wallet_recharge_request_response(r)
            payload['buyerName'] = buyer.get('name')
            payload['buyerEmail'] = buyer.get('email')
            requests.append(payload)
        
        return {"success": True, "requests": requests}
    except Exception as e:
        logging.error(f"Admin get recharge requests error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/wallet-recharge-requests/{request_id}/status")
async def admin_update_recharge_status(
    request_id: str,
    req: UpdateRechargeStatusRequest,
    current_user: dict = Depends(get_current_user)
):
    """Admin approves or rejects wallet recharge request"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if req.status not in ('approved', 'rejected'):
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'approved' or 'rejected'")
    
    try:
        # Get the recharge request
        existing = (
            supabase_admin.table('wallet_recharge_requests')
            .select('*')
            .eq('id', request_id)
            .single()
            .execute()
        )
        
        recharge = existing.data
        if not recharge:
            raise HTTPException(status_code=404, detail="Recharge request not found")
        
        if recharge.get('status') != 'pending':
            raise HTTPException(status_code=400, detail="Only pending requests can be updated")
        
        update_data = {
            'status': req.status,
            'adminId': current_user['id'],
            'adminActionTimestamp': datetime.now(timezone.utc).isoformat(),
            'updatedAt': datetime.now(timezone.utc).isoformat()
        }
        
        if req.adminNote is not None:
            update_data['adminNote'] = req.adminNote
        
        # Update the request
        result = (
            supabase_admin.table('wallet_recharge_requests')
            .update(update_data)
            .eq('id', request_id)
            .execute()
        )
        
        updated = result.data[0] if result.data else {**recharge, **update_data}
        
        # If approved, add balance to buyer wallet
        if req.status == 'approved':
            buyer_id = recharge.get('buyerId') or recharge.get('buyer_id')
            amount = float(recharge.get('amount', 0))
            
            wallet = await get_or_create_buyer_wallet(buyer_id)
            current_balance = float(wallet.get('balance', 0))
            new_balance = current_balance + amount
            
            # Update wallet balance
            supabase_admin.table('buyer_wallets').update({
                'balance': new_balance,
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }).eq('userId', buyer_id).execute()
            
            # Create transaction record
            await create_wallet_transaction(
                user_id=buyer_id,
                user_role='buyer',
                transaction_type='recharge',
                amount=amount,
                previous_balance=current_balance,
                new_balance=new_balance,
                recharge_request_id=request_id,
                description=f"Wallet recharge: ${amount:.2f}"
            )
        
        return {
            "success": True,
            "rechargeRequest": format_wallet_recharge_request_response(updated)
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Admin update recharge status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/admin/store-name-requests")
async def get_store_name_requests(current_user: dict = Depends(get_current_user)):
    """Get all store name change requests (admin only)."""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        result = supabase_admin.table('store_name_change_requests') \
            .select("*, users:seller_id(name, email)") \
            .order('created_at', desc=True).execute()

        requests = []
        for r in result.data or []:
            seller = r.get('users') or {}
            requests.append({
                "id": r.get('id'),
                "sellerId": r.get('seller_id'),
                "sellerName": seller.get('name'),
                "sellerEmail": seller.get('email'),
                "oldStoreName": r.get('old_store_name'),
                "newStoreName": r.get('new_store_name'),
                "status": r.get('status'),
                "adminNote": r.get('admin_note'),
                "createdAt": r.get('created_at'),
                "updatedAt": r.get('updated_at'),
            })

        return {"success": True, "requests": requests}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/store-name-requests/{request_id}/approve")
async def approve_store_name_request(request_id: str, action: StoreNameChangeAdminAction, current_user: dict = Depends(get_current_user)):
    """Approve a store name change request and update seller's store_name."""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        res = supabase_admin.table('store_name_change_requests').select('*').eq('id', request_id).single().execute()
        req = res.data
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")

        if req.get('status') != 'pending':
            raise HTTPException(status_code=400, detail="Only pending requests can be approved")

        new_name = req.get('new_store_name')
        if not new_name:
            raise HTTPException(status_code=400, detail="Request is missing new store name")

        # Ensure new store name is still unique
        existing = supabase_admin.table('users').select('id').eq('store_name', new_name).neq('id', req.get('seller_id')).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Store name is already used by another seller")

        # Update user store_name
        supabase_admin.table('users').update({'store_name': new_name}).eq('id', req.get('seller_id')).execute()

        # Mark this request as approved
        update_data = {
            'status': 'approved',
            'admin_id': current_user['id'],
            'admin_note': action.adminNote,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        updated = supabase_admin.table('store_name_change_requests').update(update_data).eq('id', request_id).execute()
        updated_req = updated.data[0] if updated.data else {**req, **update_data}

        return {
            "success": True,
            "request": {
                "id": updated_req.get('id'),
                "sellerId": updated_req.get('seller_id'),
                "oldStoreName": updated_req.get('old_store_name'),
                "newStoreName": updated_req.get('new_store_name'),
                "status": updated_req.get('status'),
                "adminNote": updated_req.get('admin_note'),
                "updatedAt": updated_req.get('updated_at'),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/admin/store-name-requests/{request_id}/reject")
async def reject_store_name_request(request_id: str, action: StoreNameChangeAdminAction, current_user: dict = Depends(get_current_user)):
    """Reject a store name change request."""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        res = supabase_admin.table('store_name_change_requests').select('*').eq('id', request_id).single().execute()
        req = res.data
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")

        if req.get('status') != 'pending':
            raise HTTPException(status_code=400, detail="Only pending requests can be rejected")

        update_data = {
            'status': 'rejected',
            'admin_id': current_user['id'],
            'admin_note': action.adminNote,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        updated = supabase_admin.table('store_name_change_requests').update(update_data).eq('id', request_id).execute()
        updated_req = updated.data[0] if updated.data else {**req, **update_data}

        return {
            "success": True,
            "request": {
                "id": updated_req.get('id'),
                "sellerId": updated_req.get('seller_id'),
                "oldStoreName": updated_req.get('old_store_name'),
                "newStoreName": updated_req.get('new_store_name'),
                "status": updated_req.get('status'),
                "adminNote": updated_req.get('admin_note'),
                "updatedAt": updated_req.get('updated_at'),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# SELLER ORDER CENTER ENDPOINTS
# ============================================

# Pydantic models for Order Center
class ShipOrderRequest(BaseModel):
    trackingNumber: str
    courierName: str
    courierCode: Optional[str] = None
    estimatedDelivery: Optional[str] = None
    deliveryNotes: Optional[str] = None


class UpdateShipmentRequest(BaseModel):
    trackingNumber: Optional[str] = None
    courierName: Optional[str] = None
    deliveryStatus: Optional[str] = None
    deliveryNotes: Optional[str] = None


class RefundActionRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")
    sellerResponse: Optional[str] = None
    approvedAmount: Optional[float] = None


class CreateRefundRequest(BaseModel):
    orderId: str
    reason: str
    description: Optional[str] = None
    refundType: Optional[str] = 'refund'
    requestedAmount: Optional[float] = None


# Available courier options
COURIER_OPTIONS = [
    {"code": "dhl", "name": "DHL Express", "icon": "📦"},
    {"code": "fedex", "name": "FedEx", "icon": "📫"},
    {"code": "ups", "name": "UPS", "icon": "📬"},
    {"code": "aramex", "name": "Aramex", "icon": "🚚"},
    {"code": "smsa", "name": "SMSA Express", "icon": "📮"},
    {"code": "sf_express", "name": "SF Express", "icon": "🏃"},
    {"code": "other", "name": "Other Courier", "icon": "📨"},
]


def format_shipment_response(shipment_data: dict) -> dict:
    """Format shipment data for frontend"""
    return {
        "id": shipment_data.get("id"),
        "orderId": shipment_data.get("order_id"),
        "trackingNumber": shipment_data.get("tracking_number"),
        "courierName": shipment_data.get("courier_name"),
        "courierCode": shipment_data.get("courier_code"),
        "shippedAt": shipment_data.get("shipped_at"),
        "estimatedDelivery": shipment_data.get("estimated_delivery"),
        "deliveryStatus": shipment_data.get("delivery_status"),
        "deliveryNotes": shipment_data.get("delivery_notes"),
        "createdAt": shipment_data.get("created_at"),
        "updatedAt": shipment_data.get("updated_at"),
    }


def format_refund_response(refund_data: dict) -> dict:
    """Format refund data for frontend"""
    result = {
        "id": refund_data.get("id"),
        "orderId": refund_data.get("order_id"),
        "buyerId": refund_data.get("buyer_id"),
        "sellerId": refund_data.get("seller_id"),
        "refundType": refund_data.get("refund_type"),
        "reason": refund_data.get("reason"),
        "description": refund_data.get("description"),
        "evidenceUrls": refund_data.get("evidence_urls", []),
        "requestedAmount": float(refund_data.get("requested_amount", 0)) if refund_data.get("requested_amount") else None,
        "approvedAmount": float(refund_data.get("approved_amount", 0)) if refund_data.get("approved_amount") else None,
        "status": refund_data.get("status"),
        "sellerResponse": refund_data.get("seller_response"),
        "sellerRespondedAt": refund_data.get("seller_responded_at"),
        "adminNote": refund_data.get("admin_note"),
        "resolvedAt": refund_data.get("resolved_at"),
        "createdAt": refund_data.get("created_at"),
        "updatedAt": refund_data.get("updated_at"),
    }
    # Include buyer info if available
    if 'users' in refund_data and refund_data['users']:
        result['buyer'] = {
            'name': refund_data['users'].get('name'),
            'email': refund_data['users'].get('email'),
        }
    return result


def format_order_center_response(order_data: dict, include_shipment: bool = True) -> dict:
    """Format order data for Order Center with additional fields"""
    result = format_order_response(order_data)
    result['orderStatus'] = order_data.get('order_status') or order_data.get('orderStatus') or 'pending_payment'
    result['sellerId'] = order_data.get('seller_id')
    
    # Include shipment info if available
    if include_shipment and 'shipments' in order_data and order_data['shipments']:
        shipments = order_data['shipments']
        if isinstance(shipments, list) and len(shipments) > 0:
            result['shipment'] = format_shipment_response(shipments[0])
        elif isinstance(shipments, dict):
            result['shipment'] = format_shipment_response(shipments)
    
    # Include refund info if available
    if 'refunds' in order_data and order_data['refunds']:
        refunds = order_data['refunds']
        if isinstance(refunds, list):
            result['refunds'] = [format_refund_response(r) for r in refunds]
        elif isinstance(refunds, dict):
            result['refunds'] = [format_refund_response(refunds)]
    
    # Include buyer info if available
    if 'users' in order_data and order_data['users']:
        result['buyer'] = {
            'name': order_data['users'].get('name'),
            'email': order_data['users'].get('email'),
        }
    
    return result


@api_router.get("/couriers")
async def get_courier_options():
    """Get available courier options for shipping"""
    return {"success": True, "couriers": COURIER_OPTIONS}


@api_router.get("/seller/order-center")
async def get_seller_order_center(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get seller's orders for Order Center with counts per status (NEW STORE SYSTEM)"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can access Order Center")
    
    try:
        # Get all orders with items
        all_orders_result = supabase_admin.table('orders')\
            .select('*, order_items(*), shipments(*), refunds(*), users!buyer_id(name, email)')\
            .execute()
        
        # Filter orders that contain seller's products (NEW SYSTEM: check store_products)
        seller_orders = []
        for order in all_orders_result.data or []:
            # Check if any order item belongs to seller's store products
            has_seller_item = False
            seller_items = []
            
            for item in order.get('order_items', []):
                product_id = item.get('product_id')
                if product_id:
                    # Check if this product_id is a store_product belonging to this seller
                    # NOTE: Don't filter by is_active - we want to show ALL orders including inactive products
                    store_product = supabase_admin.table('store_products')\
                        .select('id, catalog_product_id, price, stock, seller_id, product_catalog(name, description, images, category)')\
                        .eq('seller_id', current_user['id'])\
                        .eq('id', product_id)\
                        .execute()
                    
                    if store_product.data:
                        # Add product info to item
                        sp = store_product.data[0]
                        catalog_info = sp.get('product_catalog', {})
                        item['products'] = {
                            'id': sp['id'],
                            'title': catalog_info.get('name') if catalog_info else 'Product',
                            'description': catalog_info.get('description') if catalog_info else '',
                            'images': catalog_info.get('images', []) if catalog_info else [],
                            'category': catalog_info.get('category') if catalog_info else '',
                            'price': sp.get('price')
                        }
                        has_seller_item = True
                        seller_items.append(item)
            
            if has_seller_item:
                # Only include seller's items in the order
                order['order_items'] = seller_items
                
                # Fetch deposit info for this order and seller
                try:
                    deposit_result = supabase_admin.table('order_deposits')\
                        .select('*')\
                        .eq('order_id', order['id'])\
                        .eq('seller_id', current_user['id'])\
                        .execute()
                    
                    if deposit_result.data:
                        deposit = deposit_result.data[0]
                        order['depositInfo'] = {
                            'requiredAmount': float(deposit.get('required_amount', 0)),
                            'depositedAmount': float(deposit.get('deposited_amount', 0)),
                            'isComplete': deposit.get('is_deposit_complete', False),
                            'depositStatus': deposit.get('deposit_status'),
                            'depositMethod': deposit.get('deposit_method'),
                            'transactionHash': deposit.get('transaction_hash'),
                            'submittedAt': deposit.get('submitted_at')
                        }
                    else:
                        order['depositInfo'] = None
                except Exception as e:
                    logging.warning(f"Could not fetch deposit info for order {order['id']}: {str(e)}")
                    order['depositInfo'] = None
                
                seller_orders.append(order)
        
        # Calculate counts per status
        status_counts = {
            'pending_payment': 0,
            'to_be_shipped': 0,
            'to_be_received': 0,
            'to_be_evaluated': 0,
            'after_sales': 0,
            'completed': 0,
        }
        
        for order in seller_orders:
            order_status = order.get('order_status') or 'pending_payment'
            payment_status = order.get('payment_status')
            
            # Determine effective status
            if payment_status == 'pending_payment' or order_status == 'pending_payment':
                effective_status = 'pending_payment'
            elif order_status in status_counts:
                effective_status = order_status
            elif payment_status == 'paid' and (not order_status or order_status == 'pending_payment'):
                effective_status = 'to_be_shipped'
            else:
                effective_status = order_status or 'pending_payment'
            
            if effective_status in status_counts:
                status_counts[effective_status] += 1
        
        # Filter by status if provided
        filtered_orders = seller_orders
        if status:
            filtered_orders = []
            for order in seller_orders:
                order_status = order.get('order_status') or 'pending_payment'
                payment_status = order.get('payment_status')
                
                if status == 'pending_payment':
                    if payment_status == 'pending_payment' or order_status == 'pending_payment':
                        filtered_orders.append(order)
                elif status == 'to_be_shipped':
                    if payment_status == 'paid' and order_status in ('pending_payment', 'to_be_shipped', None):
                        filtered_orders.append(order)
                elif status == 'after_sales':
                    # Include orders with pending refunds
                    refunds = order.get('refunds', [])
                    has_pending_refund = any(r.get('status') in ('pending', 'seller_review') for r in (refunds if isinstance(refunds, list) else [refunds] if refunds else []))
                    if order_status == 'after_sales' or has_pending_refund:
                        filtered_orders.append(order)
                elif order_status == status:
                    filtered_orders.append(order)
        
        # Format orders for response
        formatted_orders = [format_order_center_response(o) for o in filtered_orders]
        
        return {
            "success": True,
            "orders": formatted_orders,
            "counts": status_counts,
            "total": len(seller_orders)
        }
    except Exception as e:
        logging.error(f"Get seller order center error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/seller/order-center/{order_id}")
async def get_seller_order_detail(order_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed order info for a specific order"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can access Order Center")
    
    try:
        order_result = supabase_admin.table('orders')\
            .select('*, order_items(*, products(*)), shipments(*), refunds(*, users!buyer_id(name, email)), users!buyer_id(name, email)')\
            .eq('id', order_id)\
            .execute()
        
        if not order_result.data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = order_result.data[0]
        
        # Verify seller has products in this order
        has_seller_item = False
        seller_items = []
        for item in order.get('order_items', []):
            product = item.get('products')
            if product:
                seller_product = supabase_admin.table('seller_products')\
                    .select('id')\
                    .eq('seller_id', current_user['id'])\
                    .eq('product_id', product.get('id'))\
                    .eq('is_active', True)\
                    .execute()
                
                if seller_product.data:
                    has_seller_item = True
                    seller_items.append(item)
        
        if not has_seller_item:
            raise HTTPException(status_code=403, detail="You don't have products in this order")
        
        order['order_items'] = seller_items
        
        # Fetch deposit info for this order and seller
        try:
            deposit_result = supabase_admin.table('order_deposits')\
                .select('*')\
                .eq('order_id', order_id)\
                .eq('seller_id', current_user['id'])\
                .execute()
            
            if deposit_result.data:
                deposit = deposit_result.data[0]
                order['depositInfo'] = {
                    'requiredAmount': float(deposit.get('required_amount', 0)),
                    'depositedAmount': float(deposit.get('deposited_amount', 0)),
                    'isComplete': deposit.get('is_deposit_complete', False),
                    'depositStatus': deposit.get('deposit_status'),
                    'depositMethod': deposit.get('deposit_method'),
                    'transactionHash': deposit.get('transaction_hash'),
                    'submittedAt': deposit.get('submitted_at')
                }
            else:
                order['depositInfo'] = None
        except Exception as e:
            logging.warning(f"Could not fetch deposit info for order detail {order_id}: {str(e)}")
            order['depositInfo'] = None
        
        return {"success": True, "order": format_order_center_response(order)}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get order detail error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/seller/orders/{order_id}/ship")
async def ship_order(order_id: str, req: ShipOrderRequest, current_user: dict = Depends(get_current_user)):
    """Seller ships an order - adds tracking info and updates status (NEW STORE SYSTEM)"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can ship orders")
    
    try:
        # Verify order exists
        order_result = supabase_admin.table('orders')\
            .select('*, order_items(*)')\
            .eq('id', order_id)\
            .execute()
        
        if not order_result.data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = order_result.data[0]
        
        # Verify seller owns products in this order (NEW SYSTEM: check store_products)
        has_seller_item = False
        for item in order.get('order_items', []):
            product_id = item.get('product_id')
            if product_id:
                # Check if this product_id is a store_product belonging to this seller
                store_product = supabase_admin.table('store_products')\
                    .select('id')\
                    .eq('seller_id', current_user['id'])\
                    .eq('id', product_id)\
                    .eq('is_active', True)\
                    .execute()
                
                if store_product.data:
                    has_seller_item = True
                    break
        
        if not has_seller_item:
            raise HTTPException(status_code=403, detail="You don't have products in this order")
        
        # Check order status - must be paid/to_be_shipped
        payment_status = order.get('payment_status')
        order_status = order.get('order_status')
        
        if payment_status != 'paid' and order_status != 'to_be_shipped':
            raise HTTPException(status_code=400, detail="Order must be paid before shipping")
        
        # Create shipment record
        shipment_data = {
            'id': str(uuid.uuid4()),
            'order_id': order_id,
            'tracking_number': req.trackingNumber,
            'courier_name': req.courierName,
            'courier_code': req.courierCode,
            'shipped_at': datetime.now(timezone.utc).isoformat(),
            'estimated_delivery': req.estimatedDelivery,
            'delivery_status': 'picked_up',
            'delivery_notes': req.deliveryNotes,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }
        
        # Check if shipment already exists
        existing_shipment = supabase_admin.table('shipments').select('id').eq('order_id', order_id).execute()
        
        if existing_shipment.data:
            # Update existing shipment
            supabase_admin.table('shipments').update({
                'tracking_number': req.trackingNumber,
                'courier_name': req.courierName,
                'courier_code': req.courierCode,
                'shipped_at': datetime.now(timezone.utc).isoformat(),
                'delivery_status': 'picked_up',
                'updated_at': datetime.now(timezone.utc).isoformat(),
            }).eq('order_id', order_id).execute()
        else:
            # Insert new shipment
            supabase_admin.table('shipments').insert(shipment_data).execute()
        
        # Update order status to 'to_be_received'
        supabase_admin.table('orders').update({
            'order_status': 'to_be_received',
            'seller_id': current_user['id']  # Set seller_id if not already set
        }).eq('id', order_id).execute()
        
        return {
            "success": True,
            "message": "Order shipped successfully",
            "shipment": format_shipment_response(shipment_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Ship order error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.put("/seller/orders/{order_id}/shipment")
async def update_shipment(order_id: str, req: UpdateShipmentRequest, current_user: dict = Depends(get_current_user)):
    """Update shipment tracking info"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can update shipments")
    
    try:
        # Verify shipment exists
        shipment_result = supabase_admin.table('shipments').select('*').eq('order_id', order_id).execute()
        
        if not shipment_result.data:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        update_data = {'updated_at': datetime.now(timezone.utc).isoformat()}
        if req.trackingNumber is not None:
            update_data['tracking_number'] = req.trackingNumber
        if req.courierName is not None:
            update_data['courier_name'] = req.courierName
        if req.deliveryStatus is not None:
            update_data['delivery_status'] = req.deliveryStatus
            # If marked as delivered, update order status
            if req.deliveryStatus == 'delivered':
                supabase_admin.table('orders').update({
                    'order_status': 'to_be_evaluated'
                }).eq('id', order_id).execute()
        if req.deliveryNotes is not None:
            update_data['delivery_notes'] = req.deliveryNotes
        
        result = supabase_admin.table('shipments').update(update_data).eq('order_id', order_id).execute()
        
        return {"success": True, "shipment": format_shipment_response(result.data[0])}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Update shipment error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/seller/refunds")
async def get_seller_refunds(status: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Get refund requests for seller's orders"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can view refunds")
    
    try:
        # Get orders that contain seller's products first (NEW SYSTEM: use store_products)
        all_orders_result = supabase_admin.table('orders')\
            .select('id, order_items(*)')\
            .execute()
        
        seller_order_ids = []
        for order in all_orders_result.data or []:
            for item in order.get('order_items', []):
                product_id = item.get('product_id')  # This is now store_product_id
                if product_id:
                    # Check if this store_product belongs to the seller
                    store_product = supabase_admin.table('store_products')\
                        .select('id')\
                        .eq('seller_id', current_user['id'])\
                        .eq('id', product_id)\
                        .eq('is_active', True)\
                        .execute()
                    if store_product.data:
                        seller_order_ids.append(order['id'])
                        break
        
        if not seller_order_ids:
            return {"success": True, "refunds": [], "counts": {"pending": 0, "approved": 0, "rejected": 0, "completed": 0}}
        
        # Get refunds for seller's orders
        query = supabase_admin.table('refunds')\
            .select('*, users!buyer_id(name, email), orders!order_id(id, total_amount, created_at)')\
            .in_('order_id', seller_order_ids)
        
        if status:
            query = query.eq('status', status)
        
        refunds_result = query.order('created_at', desc=True).execute()
        
        # Calculate counts
        all_refunds = supabase_admin.table('refunds').select('status').in_('order_id', seller_order_ids).execute()
        counts = {"pending": 0, "seller_review": 0, "approved": 0, "rejected": 0, "processing": 0, "completed": 0}
        for r in all_refunds.data or []:
            s = r.get('status')
            if s in counts:
                counts[s] += 1
        
        formatted_refunds = []
        for refund in refunds_result.data or []:
            formatted = format_refund_response(refund)
            if 'orders' in refund and refund['orders']:
                formatted['order'] = {
                    'id': refund['orders'].get('id'),
                    'totalAmount': refund['orders'].get('total_amount'),
                    'createdAt': refund['orders'].get('created_at'),
                }
            formatted_refunds.append(formatted)
        
        return {
            "success": True,
            "refunds": formatted_refunds,
            "counts": counts
        }
    except Exception as e:
        logging.error(f"Get seller refunds error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/seller/refunds/{refund_id}")
async def respond_to_refund(refund_id: str, req: RefundActionRequest, current_user: dict = Depends(get_current_user)):
    """Seller approves or rejects a refund request"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can respond to refunds")
    
    try:
        # Get refund
        refund_result = supabase_admin.table('refunds').select('*').eq('id', refund_id).execute()
        
        if not refund_result.data:
            raise HTTPException(status_code=404, detail="Refund request not found")
        
        refund = refund_result.data[0]
        
        # Verify seller owns products in the order (NEW SYSTEM: use store_products)
        order_result = supabase_admin.table('orders')\
            .select('*, order_items(*)')\
            .eq('id', refund['order_id'])\
            .execute()
        
        if not order_result.data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        has_seller_item = False
        for item in order_result.data[0].get('order_items', []):
            product_id = item.get('product_id')  # This is now store_product_id
            if product_id:
                # Check if this store_product belongs to the seller
                store_product = supabase_admin.table('store_products')\
                    .select('id')\
                    .eq('seller_id', current_user['id'])\
                    .eq('id', product_id)\
                    .eq('is_active', True)\
                    .execute()
                if store_product.data:
                    has_seller_item = True
                    break
        
        if not has_seller_item:
            raise HTTPException(status_code=403, detail="You cannot respond to this refund")
        
        # Update refund status
        update_data = {
            'seller_id': current_user['id'],
            'seller_response': req.sellerResponse,
            'seller_responded_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }
        
        if req.action == 'approve':
            update_data['status'] = 'approved'
            update_data['approved_amount'] = req.approvedAmount or refund.get('requested_amount')
            # Update order status
            supabase_admin.table('orders').update({
                'order_status': 'after_sales'
            }).eq('id', refund['order_id']).execute()
        else:  # reject
            update_data['status'] = 'rejected'
        
        result = supabase_admin.table('refunds').update(update_data).eq('id', refund_id).execute()
        
        return {"success": True, "refund": format_refund_response(result.data[0])}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Respond to refund error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/buyer/refunds")
async def create_refund_request(req: CreateRefundRequest, current_user: dict = Depends(get_current_user)):
    """Buyer creates a refund request"""
    if current_user['role'] != 'buyer':
        raise HTTPException(status_code=403, detail="Only buyers can request refunds")
    
    try:
        # Verify order belongs to buyer
        order_result = supabase_admin.table('orders')\
            .select('*, order_items(*, products(*))')\
            .eq('id', req.orderId)\
            .eq('buyer_id', current_user['id'])\
            .execute()
        
        if not order_result.data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = order_result.data[0]
        
        # Check if refund already exists for this order
        existing_refund = supabase_admin.table('refunds')\
            .select('id')\
            .eq('order_id', req.orderId)\
            .in_('status', ['pending', 'seller_review', 'processing'])\
            .execute()
        
        if existing_refund.data:
            raise HTTPException(status_code=400, detail="A refund request already exists for this order")
        
        # Get seller_id from order items
        seller_id = None
        for item in order.get('order_items', []):
            product = item.get('products')
            if product:
                # Find seller who has this product in their store
                seller_product = supabase_admin.table('seller_products')\
                    .select('seller_id')\
                    .eq('product_id', product.get('id'))\
                    .eq('is_active', True)\
                    .execute()
                if seller_product.data:
                    seller_id = seller_product.data[0].get('seller_id')
                    break
        
        refund_data = {
            'id': str(uuid.uuid4()),
            'order_id': req.orderId,
            'buyer_id': current_user['id'],
            'seller_id': seller_id,
            'refund_type': req.refundType or 'refund',
            'reason': req.reason,
            'description': req.description,
            'requested_amount': req.requestedAmount or float(order.get('total_amount', 0)),
            'status': 'pending',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }
        
        result = supabase_admin.table('refunds').insert(refund_data).execute()
        
        # Update order status to after_sales
        supabase_admin.table('orders').update({
            'order_status': 'after_sales'
        }).eq('id', req.orderId).execute()
        
        return {"success": True, "refund": format_refund_response(result.data[0])}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Create refund request error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/buyer/refunds")
async def get_buyer_refunds(current_user: dict = Depends(get_current_user)):
    """Get buyer's refund requests"""
    if current_user['role'] != 'buyer':
        raise HTTPException(status_code=403, detail="Only buyers can view their refunds")
    
    try:
        refunds_result = supabase_admin.table('refunds')\
            .select('*, orders!order_id(id, total_amount, created_at, order_items(*, products(*)))')\
            .eq('buyer_id', current_user['id'])\
            .order('created_at', desc=True)\
            .execute()
        
        formatted_refunds = []
        for refund in refunds_result.data or []:
            formatted = format_refund_response(refund)
            if 'orders' in refund and refund['orders']:
                formatted['order'] = format_order_response(refund['orders'])
            formatted_refunds.append(formatted)
        
        return {"success": True, "refunds": formatted_refunds}
    except Exception as e:
        logging.error(f"Get buyer refunds error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/seller/orders/{order_id}/status")
async def update_seller_order_status(order_id: str, status: str, current_user: dict = Depends(get_current_user)):
    """Seller updates order status"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can update order status")
    
    valid_statuses = ['to_be_shipped', 'to_be_received', 'to_be_evaluated', 'completed']
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    try:
        # Verify order and seller ownership
        order_result = supabase_admin.table('orders')\
            .select('*, order_items(*, products(*))')\
            .eq('id', order_id)\
            .execute()
        
        if not order_result.data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = order_result.data[0]
        
        has_seller_item = False
        for item in order.get('order_items', []):
            product = item.get('products')
            if product:
                seller_product = supabase_admin.table('seller_products')\
                    .select('id')\
                    .eq('seller_id', current_user['id'])\
                    .eq('product_id', product.get('id'))\
                    .eq('is_active', True)\
                    .execute()
                if seller_product.data:
                    has_seller_item = True
                    break
        
        if not has_seller_item:
            raise HTTPException(status_code=403, detail="You cannot update this order")
        
        # Update order status
        update_data = {
            'order_status': status,
            'seller_id': current_user['id']
        }
        
        # If completing order, also update payment_status
        if status == 'completed':
            update_data['payment_status'] = 'completed'
        
        result = supabase_admin.table('orders').update(update_data).eq('id', order_id).execute()
        
        return {"success": True, "order": format_order_center_response(result.data[0], include_shipment=False)}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Update order status error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# =====================================================
# SHIPPING ADDRESS ENDPOINTS
# =====================================================

@api_router.get("/buyer/addresses")
async def get_buyer_addresses(current_user: dict = Depends(get_current_user)):
    """Get all addresses for the current user (any authenticated user can have addresses)"""
    try:
        # Any authenticated user can have shipping addresses
        # Removed strict buyer-only check to allow sellers/admins to also have addresses
        user_id = current_user['id']
        
        # Get all addresses for user
        result = supabase_admin.table('addresses').select('*').eq('user_id', user_id).order('is_default', desc=True).order('created_at', desc=True).execute()
        
        # Format response
        addresses = []
        for addr in result.data:
            addresses.append({
                'id': addr['id'],
                'userId': addr['user_id'],
                'fullName': addr['full_name'],
                'phone': addr['phone'],
                'addressLine1': addr['address_line_1'],
                'addressLine2': addr.get('address_line_2'),
                'city': addr['city'],
                'state': addr['state'],
                'postalCode': addr['postal_code'],
                'country': addr['country'],
                'isDefault': addr.get('is_default', False),
                'createdAt': addr['created_at']
            })
        
        return {
            "success": True,
            "addresses": addresses
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get addresses error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/buyer/addresses")
async def create_address(req: CreateAddressRequest, current_user: dict = Depends(get_current_user)):
    """Create a new shipping address (any authenticated user)"""
    try:
        # Any authenticated user can create shipping addresses
        # Removed strict buyer-only check to allow sellers/admins to also create addresses
        user_id = current_user['id']
        
        # If this is set as default, we need to unset other defaults
        # This is handled by the database trigger
        
        data = {
            'user_id': user_id,
            'full_name': req.fullName,
            'phone': req.phone,
            'address_line_1': req.addressLine1,
            'address_line_2': req.addressLine2,
            'city': req.city,
            'state': req.state,
            'postal_code': req.postalCode,
            'country': req.country,
            'is_default': req.isDefault
        }
        
        result = supabase_admin.table('addresses').insert(data).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Failed to create address")
        
        addr = result.data[0]
        
        return {
            "success": True,
            "message": "Address created successfully",
            "address": {
                'id': addr['id'],
                'userId': addr['user_id'],
                'fullName': addr['full_name'],
                'phone': addr['phone'],
                'addressLine1': addr['address_line_1'],
                'addressLine2': addr.get('address_line_2'),
                'city': addr['city'],
                'state': addr['state'],
                'postalCode': addr['postal_code'],
                'country': addr['country'],
                'isDefault': addr.get('is_default', False),
                'createdAt': addr['created_at']
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Create address error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.put("/buyer/addresses/{address_id}")
async def update_address(address_id: str, req: UpdateAddressRequest, current_user: dict = Depends(get_current_user)):
    """Update a shipping address (any authenticated user)"""
    try:
        # Any authenticated user can update their own addresses
        # Removed strict buyer-only check
        user_id = current_user['id']
        
        user_id = current_user['id']
        
        # Build update data
        update_data = {}
        if req.fullName is not None:
            update_data['full_name'] = req.fullName
        if req.phone is not None:
            update_data['phone'] = req.phone
        if req.addressLine1 is not None:
            update_data['address_line_1'] = req.addressLine1
        if req.addressLine2 is not None:
            update_data['address_line_2'] = req.addressLine2
        if req.city is not None:
            update_data['city'] = req.city
        if req.state is not None:
            update_data['state'] = req.state
        if req.postalCode is not None:
            update_data['postal_code'] = req.postalCode
        if req.country is not None:
            update_data['country'] = req.country
        if req.isDefault is not None:
            update_data['is_default'] = req.isDefault
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Update address (RLS ensures only own addresses)
        result = supabase_admin.table('addresses').update(update_data).eq('id', address_id).eq('user_id', user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Address not found")
        
        return {
            "success": True,
            "message": "Address updated successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Update address error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.delete("/buyer/addresses/{address_id}")
async def delete_address(address_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a shipping address (any authenticated user)"""
    try:
        # Any authenticated user can delete their own addresses
        # Removed strict buyer-only check
        user_id = current_user['id']
        
        # Delete address (RLS ensures only own addresses)
        result = supabase_admin.table('addresses').delete().eq('id', address_id).eq('user_id', user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Address not found")
        
        return {
            "success": True,
            "message": "Address deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Delete address error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# =====================================================
# END SHIPPING ADDRESS ENDPOINTS
# =====================================================

# =====================================================
# STORE SYSTEM ENDPOINTS (BUYER STORE SEARCH & DETAIL)
# =====================================================

@api_router.post("/admin/seed-catalog")
@limiter.limit("5/hour")
async def seed_product_catalog(request: Request, current_user: dict = Depends(get_current_user)):
    """Admin-only: Seed the product catalog with 100 products"""
    try:
        # Check admin role
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Import catalog
        from product_catalog import PRODUCT_CATALOG
        
        # Check if already seeded
        existing = supabase_admin.table('product_catalog').select('id').limit(1).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Catalog already seeded. Delete existing products first.")
        
        # Insert all products
        catalog_items = []
        for product in PRODUCT_CATALOG:
            catalog_items.append({
                'name': product['title'],
                'description': product['description'],
                'base_price': product['price'],
                'images': product['images'],
                'category': product['category']
            })
        
        result = supabase_admin.table('product_catalog').insert(catalog_items).execute()
        
        return {
            "success": True,
            "message": f"Successfully seeded {len(result.data)} products to catalog"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Seed catalog error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.delete("/admin/clear-catalog")
@limiter.limit("5/hour")
async def clear_product_catalog_new(request: Request, current_user: dict = Depends(get_current_user)):
    """Admin-only: Clear product_catalog table (for re-seeding)"""
    try:
        # Check admin role
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # First delete all store_products that reference catalog products
        supabase_admin.table('store_products').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        
        # Then delete all catalog products
        result = supabase_admin.table('product_catalog').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        
        return {
            "success": True,
            "message": f"Cleared product catalog and store products"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Clear catalog error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/admin/cleanup-and-reseed-catalog")
@limiter.limit("2/hour")
async def cleanup_and_reseed_catalog(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Admin-only: Intelligent catalog cleanup and reseed
    1. Keeps catalog products already in seller stores
    2. Deletes unused catalog products
    3. Seeds 500 new unique products
    """
    try:
        # Check admin role
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        #  Step 1: Find which catalog products are in use
        store_products_result = supabase_admin.table('store_products').select('catalog_product_id').execute()
        in_use_ids = set([sp['catalog_product_id'] for sp in (store_products_result.data or []) if sp.get('catalog_product_id')])
        
        # Step 2: Get all catalog products
        all_catalog_result = supabase_admin.table('product_catalog').select('id').execute()
        all_ids = [p['id'] for p in (all_catalog_result.data or [])]
        
        # Step 3: Delete unused products
        to_delete = [pid for pid in all_ids if pid not in in_use_ids]
        deleted_count = 0
        if to_delete:
            # Delete in batches of 100
            for i in range(0, len(to_delete), 100):
                batch = to_delete[i:i+100]
                supabase_admin.table('product_catalog').delete().in_('id', batch).execute()
                deleted_count += len(batch)
        
        # Step 4: Seed 150 new products (keeping it manageable, can be increased)
        from new_catalog_500 import get_unique_products
        new_products = get_unique_products(150)  # Get 150 unique products
        
        added_count = 0
        for product in new_products:
            try:
                supabase_admin.table('product_catalog').insert(product).execute()
                added_count += 1
            except Exception as e:
                logging.error(f"Error adding product {product['name']}: {str(e)}")
        
        return {
            "success": True,
            "kept": len(in_use_ids),
            "deleted": deleted_count,
            "added": added_count,
            "total_catalog_size": len(in_use_ids) + added_count,
            "message": f"Cleanup complete! Kept {len(in_use_ids)} products in use, deleted {deleted_count} unused products, added {added_count} new products"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Clear catalog error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/stores/search")
async def search_stores(query: Optional[str] = None, limit: int = 20, offset: int = 0, current_user: dict = Depends(get_current_user)):
    """Protected: Search stores by name (login required)"""
    try:
        # Build query
        db_query = supabase.table('stores').select('id, seller_id, store_name, status, created_at')
        
        # Only active stores
        db_query = db_query.eq('status', 'active')
        
        # Filter by name if provided
        if query:
            db_query = db_query.ilike('store_name', f'%{query}%')
        
        # Pagination
        db_query = db_query.range(offset, offset + limit - 1).order('store_name')
        
        result = db_query.execute()
        
        # Format response
        stores = []
        for store in result.data:
            stores.append({
                'id': store['id'],
                'sellerId': store['seller_id'],
                'storeName': store['store_name'],
                'status': store['status'],
                'createdAt': store['created_at']
            })
        
        return {
            "success": True,
            "stores": stores,
            "total": len(stores)
        }
    
    except Exception as e:
        logging.error(f"Search stores error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/stores/{store_id}")
async def get_store_detail(store_id: str, current_user: dict = Depends(get_current_user)):
    """Protected: Get store details (login required)"""
    try:
        # Get store info with seller details
        result = supabase.table('stores').select(
            'id, seller_id, store_name, status, created_at, users:seller_id(name, email, verification_status)'
        ).eq('id', store_id).eq('status', 'active').single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Store not found or inactive")
        
        store = result.data
        
        # Format response
        store_data = {
            'id': store['id'],
            'sellerId': store['seller_id'],
            'storeName': store['store_name'],
            'status': store['status'],
            'createdAt': store['created_at']
        }
        
        if store.get('users'):
            store_data['seller'] = {
                'name': store['users'].get('name'),
                'email': store['users'].get('email'),
                'verificationStatus': store['users'].get('verification_status')
            }
        
        return {
            "success": True,
            "store": store_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get store detail error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/stores/{store_id}/products")
async def get_store_products(store_id: str, limit: int = 50, offset: int = 0, current_user: dict = Depends(get_current_user)):
    """
    Protected: Get products from a specific store (login required)
    CRITICAL: This joins store_products with product_catalog
    Buyers can ONLY see what's in store_products, NOT the full catalog
    """
    try:
        # Get store products with catalog info
        # IMPORTANT: Query starts from store_products, NOT product_catalog
        # Use admin client to bypass RLS for reading catalog info
        result = supabase_admin.table('store_products').select(
            '''
            id,
            store_id,
            seller_id,
            catalog_product_id,
            price,
            stock,
            custom_description,
            is_active,
            created_at,
            product_catalog:catalog_product_id(name, description, base_price, images, category)
            '''
        ).eq('store_id', store_id).eq('is_active', True).range(offset, offset + limit - 1).order('created_at', desc=True).execute()
        
        # Format response
        products = []
        for item in result.data:
            catalog_info = item.get('product_catalog', {})
            
            products.append({
                'id': item['id'],
                'storeId': item['store_id'],
                'sellerId': item['seller_id'],
                'catalogProductId': item['catalog_product_id'],
                'price': float(item['price']),  # Store-specific price
                'stock': item['stock'],
                'customDescription': item['custom_description'],
                'isActive': item['is_active'],
                'createdAt': item['created_at'],
                # Catalog info (name, images from master catalog)
                'name': catalog_info.get('name'),
                'description': item['custom_description'] or catalog_info.get('description'),
                'basePrice': float(catalog_info.get('base_price', 0)),
                'images': catalog_info.get('images', []),
                'category': catalog_info.get('category')
            })
        
        return {
            "success": True,
            "products": products,
            "total": len(products)
        }
    
    except Exception as e:
        logging.error(f"Get store products error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/seller/catalog/products")
async def get_catalog_products_for_seller(
    current_user: dict = Depends(get_current_user),
    category: Optional[str] = None,
    limit: int = 200,  # Increased to show more products
    offset: int = 0
):
    """
    Seller-only: Browse product catalog to add products to their store
    Buyers CANNOT access this endpoint (enforced by RLS)
    IMPORTANT: Filters out products already added by ANY seller to prevent duplicates
    """
    try:
        # Verify seller role
        if current_user.get('role') != 'seller':
            raise HTTPException(status_code=403, detail="Seller access required")
        
        # Get all catalog product IDs that are already in use by ANY seller
        store_products_result = supabase_admin.table('store_products').select('catalog_product_id').execute()
        used_catalog_ids = set([sp['catalog_product_id'] for sp in (store_products_result.data or []) if sp.get('catalog_product_id')])
        
        # Query catalog (RLS enforces seller-only access)
        query = supabase.table('product_catalog').select('*')
        
        if category:
            query = query.eq('category', category)
        
        # Get more products than needed since we'll filter some out
        query = query.limit(limit * 3).order('name')
        result = query.execute()
        
        # Format response and filter out already-used products
        products = []
        for product in result.data:
            # Skip products that are already in any seller's store
            if product['id'] in used_catalog_ids:
                continue
                
            products.append({
                'id': product['id'],
                'name': product['name'],
                'description': product['description'],
                'basePrice': float(product['base_price']),
                'images': product['images'],
                'category': product['category'],
                'createdAt': product['created_at']
            })
            
            # Stop when we have enough products
            if len(products) >= limit:
                break
        
        return {
            "success": True,
            "products": products,
            "total": len(products)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get catalog products error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/seller/store/products")
async def add_product_to_store(
    catalog_product_id: str = Form(...),
    price: float = Form(...),
    stock: int = Form(0),
    custom_description: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Seller-only: Add a catalog product to their store"""
    try:
        # Verify seller role
        if current_user.get('role') != 'seller':
            raise HTTPException(status_code=403, detail="Seller access required")
        
        seller_id = current_user['id']
        
        # Get or create seller's store
        store_result = supabase_admin.table('stores').select('id').eq('seller_id', seller_id).execute()
        
        if not store_result.data or len(store_result.data) == 0:
            # Auto-create store if it doesn't exist
            store_name = current_user.get('store_name') or current_user.get('name', 'Seller') + "'s Store"
            
            new_store = supabase_admin.table('stores').insert({
                'seller_id': seller_id,
                'store_name': store_name,
                'status': 'active'
            }).execute()
            
            if not new_store.data:
                raise HTTPException(status_code=500, detail="Failed to create store")
            
            store_id = new_store.data[0]['id']
            logging.info(f"Auto-created store for seller {seller_id}: {store_name}")
        else:
            store_id = store_result.data[0]['id']
        
        # Check if product already in store
        existing = supabase_admin.table('store_products').select('id').eq('store_id', store_id).eq('catalog_product_id', catalog_product_id).execute()
        
        if existing.data:
            raise HTTPException(status_code=400, detail="Product already in your store")
        
        # Add product to store
        data = {
            'store_id': store_id,
            'seller_id': seller_id,
            'catalog_product_id': catalog_product_id,
            'price': price,
            'stock': stock,
            'custom_description': custom_description,
            'is_active': True
        }
        
        result = supabase_admin.table('store_products').insert(data).execute()
        
        return {
            "success": True,
            "message": "Product added to store successfully",
            "storeProduct": result.data[0] if result.data else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Add product to store error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/seller/store/products")
async def get_my_store_products(current_user: dict = Depends(get_current_user)):
    """Seller-only: Get all products in their store"""
    try:
        # Verify seller role
        if current_user.get('role') != 'seller':
            raise HTTPException(status_code=403, detail="Seller access required")
        
        seller_id = current_user['id']
        
        # Get store products with catalog info
        result = supabase_admin.table('store_products').select(
            '''
            id,
            store_id,
            seller_id,
            catalog_product_id,
            price,
            stock,
            custom_description,
            is_active,
            created_at,
            product_catalog:catalog_product_id(name, description, base_price, images, category)
            '''
        ).eq('seller_id', seller_id).order('created_at', desc=True).execute()
        
        # Format response
        products = []
        for item in result.data:
            catalog_info = item.get('product_catalog', {})
            
            products.append({
                'id': item['id'],
                'storeId': item['store_id'],
                'catalogProductId': item['catalog_product_id'],
                'price': float(item['price']),
                'stock': item['stock'],
                'customDescription': item['custom_description'],
                'isActive': item['is_active'],
                'createdAt': item['created_at'],
                'name': catalog_info.get('name'),
                'description': catalog_info.get('description'),
                'basePrice': float(catalog_info.get('base_price', 0)),
                'images': catalog_info.get('images', []),
                'category': catalog_info.get('category')
            })
        
        return {
            "success": True,
            "products": products
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get my store products error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.put("/seller/store/products/{product_id}")
async def update_store_product(
    product_id: str,
    price: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
    custom_description: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Seller-only: Update a product in their store"""
    try:
        # Verify seller role
        if current_user.get('role') != 'seller':
            raise HTTPException(status_code=403, detail="Seller access required")
        
        seller_id = current_user['id']
        
        # Build update data
        update_data = {}
        if price is not None:
            update_data['price'] = price
        if stock is not None:
            update_data['stock'] = stock
        if custom_description is not None:
            update_data['custom_description'] = custom_description
        if is_active is not None:
            update_data['is_active'] = is_active
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Update product (RLS ensures only own products)
        result = supabase_admin.table('store_products').update(update_data).eq('id', product_id).eq('seller_id', seller_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Product not found in your store")
        
        return {
            "success": True,
            "message": "Store product updated successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Update store product error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.delete("/seller/store/products/{product_id}")
async def remove_product_from_store(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Seller-only: Remove a product from their store"""
    try:
        # Verify seller role
        if current_user.get('role') != 'seller':
            raise HTTPException(status_code=403, detail="Seller access required")
        
        seller_id = current_user['id']
        
        # Delete product (RLS ensures only own products)
        result = supabase_admin.table('store_products').delete().eq('id', product_id).eq('seller_id', seller_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Product not found in your store")
        
        return {
            "success": True,
            "message": "Product removed from store successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Remove product from store error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# =====================================================
# END STORE SYSTEM ENDPOINTS
# =====================================================

@api_router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return {"success": True, "user": current_user}


# Contact Form Endpoint
@api_router.post("/contact")
async def submit_contact_form(
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    """Public endpoint to submit contact form - sends email to support"""
    try:
        # Validate email format
        if not email or '@' not in email:
            raise HTTPException(status_code=400, detail="Invalid email address")
        
        # Validate required fields
        if not name or not subject or not message:
            raise HTTPException(status_code=400, detail="All fields are required")
        
        # Create email content
        support_email = "support@arabshopping.org"
        email_subject = f"Contact Form: {subject}"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1a1a1a; color: #fff; padding: 20px;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #D4AF37;">
                <h1 style="color: #D4AF37; margin: 0;">Amazon Arab</h1>
                <p style="color: #888; margin: 5px 0 0 0;">Contact Form Submission</p>
            </div>
            
            <div style="padding: 30px 20px;">
                <h2 style="color: #D4AF37; margin-bottom: 20px;">New Contact Form Message</h2>
                
                <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px 0; color: #888; width: 120px;">Name:</td>
                            <td style="padding: 10px 0; color: #fff;"><strong>{name}</strong></td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; color: #888;">Email:</td>
                            <td style="padding: 10px 0; color: #D4AF37;"><strong>{email}</strong></td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; color: #888;">Subject:</td>
                            <td style="padding: 10px 0; color: #fff;"><strong>{subject}</strong></td>
                        </tr>
                    </table>
                </div>
                
                <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="color: #888; margin: 0 0 10px 0; font-weight: bold;">Message:</p>
                    <p style="color: #fff; line-height: 1.6; margin: 0; white-space: pre-wrap;">{message}</p>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #333; color: #888; text-align: center;">
                    <p style="margin: 5px 0; font-size: 12px;">
                        This email was sent from the Amazon Arab contact form.
                    </p>
                    <p style="margin: 5px 0; font-size: 12px;">
                        Reply directly to this email to respond to the customer at: {email}
                    </p>
                </div>
            </div>
            
            <div style="text-align: center; padding: 20px; border-top: 2px solid #D4AF37; color: #888; font-size: 12px;">
                <p style="margin: 5px 0;">© 2025 Amazon Arab. All rights reserved.</p>
                <p style="margin: 5px 0;">Premium Multi-Vendor Marketplace</p>
            </div>
        </div>
        """
        
        # Send email to support
        if RESEND_API_KEY:
            params = {
                "from": f"Amazon Arab Contact <{SENDER_EMAIL}>",
                "to": [support_email],
                "reply_to": [email],  # Allow direct reply to customer
                "subject": email_subject,
                "html": html_content
            }
            result = await asyncio.to_thread(resend.Emails.send, params)
            logging.info(f"Contact form email sent to {support_email}: {result.get('id')}")
            
            return {
                "success": True,
                "message": "Your message has been sent successfully! We'll get back to you within 24 hours."
            }
        else:
            logging.warning("RESEND_API_KEY not configured, cannot send contact form email")
            raise HTTPException(status_code=500, detail="Email service not configured")
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Contact form submission error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send message. Please try again later.")


# ============================================================================
# ESCROW + DEPOSIT SYSTEM ENDPOINTS
# ============================================================================

@api_router.get("/seller/orders/pending-deposit")
async def get_orders_pending_deposit(current_user: dict = Depends(get_current_user)):
    """Get all orders waiting for seller deposit"""
    try:
        user_id = current_user['id']
        user_role = current_user.get('role')
        
        if user_role != 'seller':
            raise HTTPException(status_code=403, detail="Seller access required")
        
        # Get orders with escrow_status = 'awaiting_seller_deposit'
        orders_result = supabase_admin.table('orders')\
            .select('*, order_items(*, store_products(*, product_catalog(*), stores(*)))')\
            .eq('escrow_status', 'awaiting_seller_deposit')\
            .execute()
        
        if not orders_result.data:
            return {"orders": [], "count": 0}
        
        # Filter orders that contain this seller's products
        seller_orders = []
        for order in orders_result.data:
            order_items = order.get('order_items', [])
            has_seller_product = False
            
            for item in order_items:
                store_product = item.get('store_products')
                if store_product:
                    store = store_product.get('stores')
                    if store and store.get('seller_id') == user_id:
                        has_seller_product = True
                        break
            
            if has_seller_product:
                # Get deposit info
                deposit_result = supabase_admin.table('order_deposits')\
                    .select('*')\
                    .eq('order_id', order['id'])\
                    .eq('seller_id', user_id)\
                    .execute()
                
                deposit_info = deposit_result.data[0] if deposit_result.data else None
                
                seller_orders.append({
                    'id': order['id'],
                    'totalAmount': float(order.get('total_amount', 0)),  # Fixed: use snake_case
                    'depositRequired': float(order.get('deposit_required', 0)),  # Fixed: use snake_case
                    'escrowStatus': order.get('escrow_status'),
                    'createdAt': order.get('created_at'),  # Fixed: use snake_case
                    'depositInfo': {
                        'requiredAmount': float(deposit_info['required_amount']) if deposit_info else 0,
                        'depositedAmount': float(deposit_info['deposited_amount']) if deposit_info else 0,
                        'isComplete': deposit_info['is_deposit_complete'] if deposit_info else False,
                        'depositStatus': deposit_info.get('deposit_status'),
                        'transactionHash': deposit_info.get('transaction_hash'),
                        'submittedAt': deposit_info.get('submitted_at')
                    } if deposit_info else None
                })
        
        return {
            "orders": seller_orders,
            "count": len(seller_orders)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get pending deposit orders error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/seller/wallet/deposit-for-order")
async def deposit_for_order(req: SellerDepositRequest, current_user: dict = Depends(get_current_user)):
    """Seller deposits money to unlock order (80% of order value)"""
    try:
        user_id = current_user['id']
        user_role = current_user.get('role')
        
        if user_role != 'seller':
            raise HTTPException(status_code=403, detail="Seller access required")
        
        # 1. Verify order exists and needs deposit
        order_result = supabase_admin.table('orders')\
            .select('*, order_items(*, store_products(stores(*)))')\
            .eq('id', req.orderId)\
            .execute()
        
        if not order_result.data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = order_result.data[0]
        
        # Verify this seller owns products in this order
        has_seller_product = False
        for item in order.get('order_items', []):
            store_product = item.get('store_products')
            if store_product:
                store = store_product.get('stores')
                if store and store.get('seller_id') == user_id:
                    has_seller_product = True
                    break
        
        if not has_seller_product:
            raise HTTPException(status_code=403, detail="This order does not contain your products")
        
        if order.get('escrow_status') != 'awaiting_seller_deposit':
            raise HTTPException(status_code=400, detail="Order is not awaiting deposit")
        
        # 2. Get or create seller wallet
        wallet_result = supabase_admin.table('seller_wallets')\
            .select('*')\
            .eq('userId', user_id)\
            .execute()
        
        if not wallet_result.data:
            # Create wallet
            create_result = supabase_admin.table('seller_wallets')\
                .insert({'userId': user_id, 'balance': 0.00, 'depositBalance': 0.00, 'withdrawableBalance': 0.00})\
                .execute()
            wallet = create_result.data[0]
        else:
            wallet = wallet_result.data[0]
        
        current_balance = float(wallet.get('balance', 0))
        deposit_balance = float(wallet.get('depositBalance', 0))
        required_deposit = float(order.get('deposit_required', 0))  # Fixed: use snake_case column name
        
        # 3. Verify seller has enough balance to deposit
        if current_balance < required_deposit:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient balance. You need ${required_deposit:.2f} but have ${current_balance:.2f}. Please recharge your wallet first."
            )
        
        # 4. Process deposit (move from balance to depositBalance)
        new_balance = current_balance - required_deposit
        new_deposit_balance = deposit_balance + required_deposit
        
        update_wallet = supabase_admin.table('seller_wallets')\
            .update({
                'balance': new_balance,
                'depositBalance': new_deposit_balance,
                'updatedAt': datetime.now(timezone.utc).isoformat()
            })\
            .eq('userId', user_id)\
            .execute()
        
        # 5. Record transaction
        supabase_admin.table('wallet_transactions').insert({
            'userId': user_id,
            'userRole': 'seller',
            'type': 'withdrawal',
            'amount': required_deposit,
            'previousBalance': current_balance,
            'newBalance': new_balance,
            'orderId': req.orderId,
            'description': f'Deposit ${required_deposit:.2f} to unlock order {req.orderId[:8]}'
        }).execute()
        
        # 6. Update order_deposits
        deposit_result = supabase_admin.table('order_deposits')\
            .select('*')\
            .eq('order_id', req.orderId)\
            .eq('seller_id', user_id)\
            .execute()
        
        # 6. Update order_deposits - set as pending for admin confirmation
        deposit_update_data = {
            'deposited_amount': required_deposit,
            'is_deposit_complete': False,  # Wait for admin confirmation
            'deposit_method': 'internal_wallet',  # Use internal_wallet to match DB constraint
            'deposit_status': 'pending',
            'submitted_at': datetime.now(timezone.utc).isoformat()
        }
        
        if deposit_result.data:
            # Update existing
            supabase_admin.table('order_deposits')\
                .update(deposit_update_data)\
                .eq('order_id', req.orderId)\
                .eq('seller_id', user_id)\
                .execute()
        else:
            # Create new
            deposit_update_data.update({
                'order_id': req.orderId,
                'seller_id': user_id,
                'required_amount': required_deposit
            })
            supabase_admin.table('order_deposits').insert(deposit_update_data).execute()
        
        # 7. Keep order status as 'awaiting_seller_deposit' until admin confirms
        # The order status will be updated to 'deposit_received' when admin confirms
        
        # 8. Notify admin about the wallet balance deposit
        try:
            if RESEND_API_KEY:
                seller_info = current_user.get('name', current_user.get('email', 'Unknown'))
                resend.Emails.send({
                    "from": SENDER_EMAIL,
                    "to": ADMIN_EMAIL,
                    "subject": f"New Wallet Deposit - Order {req.orderId[:8]}",
                    "html": f"""
                    <h2>New Wallet Balance Deposit Submitted</h2>
                    <p><strong>Seller:</strong> {seller_info}</p>
                    <p><strong>Order ID:</strong> {req.orderId}</p>
                    <p><strong>Amount:</strong> ${required_deposit:.2f} (from wallet balance)</p>
                    <p><strong>Payment Method:</strong> Wallet Balance</p>
                    <p>The seller has deposited funds from their wallet balance. Please confirm this deposit in the admin panel.</p>
                    """
                })
        except Exception as e:
            logging.warning(f"Failed to send admin notification: {str(e)}")
        
        return {
            "success": True,
            "message": f"Deposit of ${required_deposit:.2f} submitted. Awaiting admin confirmation.",
            "depositAmount": required_deposit,
            "newBalance": new_balance,
            "depositBalance": new_deposit_balance,
            "orderStatus": "awaiting_confirmation"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Deposit for order error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/seller/orders/{order_id}/submit-usdt-deposit")
async def submit_usdt_deposit_payment(
    order_id: str,
    req: SubmitUSDTDepositRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Seller submits USDT TRC20 deposit payment proof for order
    Alternative to internal wallet deposit
    """
    try:
        user_id = current_user['id']
        user_role = current_user.get('role')
        
        if user_role != 'seller':
            raise HTTPException(status_code=403, detail="Seller access required")
        
        # 1. Verify order exists and needs deposit
        order_result = supabase_admin.table('orders')\
            .select('*, order_items(*, store_products(stores(*)))')\
            .eq('id', req.orderId)\
            .execute()
        
        if not order_result.data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = order_result.data[0]
        
        # Verify this seller owns products in this order
        has_seller_product = False
        for item in order.get('order_items', []):
            store_product = item.get('store_products')
            if store_product:
                store = store_product.get('stores')
                if store and store.get('seller_id') == user_id:
                    has_seller_product = True
                    break
        
        if not has_seller_product:
            raise HTTPException(status_code=403, detail="This order does not contain your products")
        
        if order.get('escrow_status') not in ['awaiting_seller_deposit', 'deposit_received']:
            raise HTTPException(status_code=400, detail="Order is not awaiting deposit")
        
        required_deposit = float(order.get('deposit_required', 0))
        
        # 2. Get or create deposit record
        deposit_result = supabase_admin.table('order_deposits')\
            .select('*')\
            .eq('order_id', req.orderId)\
            .eq('seller_id', user_id)\
            .execute()
        
        deposit_data = {
            'deposit_method': 'usdt_payment',
            'transaction_hash': req.transactionHash,
            'payment_notes': req.notes,
            'deposit_status': 'pending',
            'submitted_at': datetime.now(timezone.utc).isoformat(),
            'deposited_amount': required_deposit
        }
        
        if deposit_result.data:
            # Update existing deposit record
            supabase_admin.table('order_deposits')\
                .update(deposit_data)\
                .eq('order_id', req.orderId)\
                .eq('seller_id', user_id)\
                .execute()
        else:
            # Create new deposit record
            deposit_data.update({
                'order_id': req.orderId,
                'seller_id': user_id,
                'required_amount': required_deposit,
                'is_deposit_complete': False
            })
            supabase_admin.table('order_deposits').insert(deposit_data).execute()
        
        # 3. Send notification to admin
        try:
            if RESEND_API_KEY:
                seller_info = current_user.get('name', current_user.get('email', 'Unknown'))
                resend.Emails.send({
                    "from": SENDER_EMAIL,
                    "to": ADMIN_EMAIL,
                    "subject": f"New USDT Deposit Submission - Order {order_id[:8]}",
                    "html": f"""
                    <h2>New USDT Deposit Payment Submitted</h2>
                    <p><strong>Seller:</strong> {seller_info}</p>
                    <p><strong>Order ID:</strong> {order_id}</p>
                    <p><strong>Amount:</strong> ${required_deposit:.2f} USDT (TRC20)</p>
                    <p><strong>Transaction Hash:</strong> {req.transactionHash}</p>
                    <p><strong>Notes:</strong> {req.notes or 'None'}</p>
                    <p><strong>Wallet Address:</strong> {ADMIN_CRYPTO_WALLET}</p>
                    <p>Please verify this transaction and confirm the deposit in the admin panel.</p>
                    """
                })
        except Exception as e:
            logging.warning(f"Failed to send admin notification: {str(e)}")
        
        return {
            "success": True,
            "message": "Deposit payment submitted successfully. Awaiting admin confirmation.",
            "depositAmount": required_deposit,
            "transactionHash": req.transactionHash,
            "status": "pending"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Submit USDT deposit error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/admin/deposit-confirmations")
async def get_pending_deposit_confirmations(current_user: dict = Depends(get_current_user)):
    """
    Admin endpoint to view all pending deposit confirmations (both USDT and wallet balance)
    """
    try:
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get all pending deposit confirmations (both USDT payment and internal wallet)
        deposits_result = supabase_admin.table('order_deposits')\
            .select('*, orders(id, total_amount, created_at, buyer_id), users!seller_id(id, name, email)')\
            .eq('deposit_status', 'pending')\
            .in_('deposit_method', ['usdt_payment', 'internal_wallet'])\
            .order('submitted_at', desc=True)\
            .execute()
        
        formatted_deposits = []
        for deposit in deposits_result.data or []:
            order_info = deposit.get('orders', {})
            seller_info = deposit.get('users', {})
            
            formatted_deposits.append({
                'id': deposit['id'],
                'orderId': deposit['order_id'],
                'sellerId': deposit['seller_id'],
                'sellerName': seller_info.get('name', 'Unknown'),
                'sellerEmail': seller_info.get('email', 'Unknown'),
                'orderAmount': float(order_info.get('total_amount', 0)),
                'depositRequired': float(deposit['required_amount']),
                'depositAmount': float(deposit.get('deposited_amount', 0)),
                'transactionHash': deposit.get('transaction_hash'),
                'notes': deposit.get('payment_notes'),
                'submittedAt': deposit.get('submitted_at'),
                'orderCreatedAt': order_info.get('created_at'),
                'depositMethod': deposit.get('deposit_method', 'unknown')  # Include deposit method for UI display
            })
        
        return {
            "success": True,
            "deposits": formatted_deposits,
            "count": len(formatted_deposits)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get deposit confirmations error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/orders/{order_id}/confirm-deposit")
async def confirm_seller_deposit(
    order_id: str,
    req: ConfirmDepositRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Admin confirms or rejects seller's USDT deposit payment
    """
    try:
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # 1. Get deposit record (both USDT and internal wallet methods)
        deposit_result = supabase_admin.table('order_deposits')\
            .select('*, users!seller_id(name, email)')\
            .eq('order_id', order_id)\
            .in_('deposit_method', ['usdt_payment', 'internal_wallet'])\
            .eq('deposit_status', 'pending')\
            .execute()
        
        if not deposit_result.data:
            raise HTTPException(status_code=404, detail="No pending deposit found for this order")
        
        deposit = deposit_result.data[0]
        seller_info = deposit.get('users', {})
        deposit_method = deposit.get('deposit_method', 'unknown')
        
        if req.approved:
            # APPROVE DEPOSIT
            # Update deposit record
            supabase_admin.table('order_deposits')\
                .update({
                    'deposit_status': 'confirmed',
                    'is_deposit_complete': True,
                    'confirmed_at': datetime.now(timezone.utc).isoformat(),
                    'confirmed_by': current_user['id']
                })\
                .eq('order_id', order_id)\
                .execute()
            
            # Update order status to deposit_received AND set order_status to 'to_be_shipped'
            # This moves the order from 'Pending Payment' to 'To Be Shipped' in Order Center
            supabase_admin.table('orders')\
                .update({
                    'escrow_status': 'deposit_received',
                    'order_status': 'to_be_shipped'  # Move to 'To Be Shipped' column in Order Center
                })\
                .eq('id', order_id)\
                .execute()
            
            # Send confirmation email to seller
            try:
                if RESEND_API_KEY and seller_info.get('email'):
                    method_display = "USDT" if deposit_method == 'usdt_payment' else "wallet balance"
                    resend.Emails.send({
                        "from": SENDER_EMAIL,
                        "to": seller_info['email'],
                        "subject": f"Deposit Confirmed - Order {order_id[:8]}",
                        "html": f"""
                        <h2>Your Deposit Has Been Confirmed!</h2>
                        <p>Hello {seller_info.get('name', 'Seller')},</p>
                        <p>Your {method_display} deposit of <strong>${float(deposit['required_amount']):.2f}</strong> has been confirmed by the admin.</p>
                        <p><strong>Order ID:</strong> {order_id}</p>
                        <p><strong>Payment Method:</strong> {method_display.title()}</p>
                        {f"<p><strong>Transaction Hash:</strong> {deposit.get('transaction_hash')}</p>" if deposit.get('transaction_hash') else ""}
                        <p>You can now ship this order. Once the order is completed, you will receive 100% of the order amount in your earnings.</p>
                        <p>Thank you for using our platform!</p>
                        """
                    })
            except Exception as e:
                logging.warning(f"Failed to send seller notification: {str(e)}")
            
            return {
                "success": True,
                "message": "Deposit confirmed successfully. Order unlocked for shipping.",
                "orderId": order_id,
                "status": "confirmed"
            }
        else:
            # REJECT DEPOSIT
            if not req.rejectionReason:
                raise HTTPException(status_code=400, detail="Rejection reason is required")
            
            supabase_admin.table('order_deposits')\
                .update({
                    'deposit_status': 'rejected',
                    'rejection_reason': req.rejectionReason,
                    'confirmed_at': datetime.now(timezone.utc).isoformat(),
                    'confirmed_by': current_user['id']
                })\
                .eq('order_id', order_id)\
                .execute()
            
            # If internal wallet deposit was rejected, return the funds to seller's wallet
            if deposit_method == 'internal_wallet':
                try:
                    seller_id = deposit.get('seller_id')
                    deposit_amount = float(deposit.get('deposited_amount', 0))
                    
                    if seller_id and deposit_amount > 0:
                        # Get seller wallet
                        wallet_result = supabase_admin.table('seller_wallets')\
                            .select('*')\
                            .eq('userId', seller_id)\
                            .execute()
                        
                        if wallet_result.data:
                            wallet = wallet_result.data[0]
                            current_balance = float(wallet.get('balance', 0))
                            current_deposit_balance = float(wallet.get('depositBalance', 0))
                            
                            # Return funds: move from depositBalance back to balance
                            new_balance = current_balance + deposit_amount
                            new_deposit_balance = max(current_deposit_balance - deposit_amount, 0)
                            
                            supabase_admin.table('seller_wallets')\
                                .update({
                                    'balance': new_balance,
                                    'depositBalance': new_deposit_balance,
                                    'updatedAt': datetime.now(timezone.utc).isoformat()
                                })\
                                .eq('userId', seller_id)\
                                .execute()
                            
                            # Record refund transaction
                            supabase_admin.table('wallet_transactions').insert({
                                'userId': seller_id,
                                'userRole': 'seller',
                                'type': 'recharge',  # Use recharge type for returning funds
                                'amount': deposit_amount,
                                'previousBalance': current_balance,
                                'newBalance': new_balance,
                                'orderId': order_id,
                                'description': f'Deposit refund - rejected by admin for order {order_id[:8]}'
                            }).execute()
                            
                            logging.info(f"Refunded ${deposit_amount:.2f} to seller {seller_id} for rejected deposit")
                except Exception as e:
                    logging.error(f"Failed to refund wallet balance deposit: {str(e)}")
            
            # Send rejection email to seller
            try:
                if RESEND_API_KEY and seller_info.get('email'):
                    method_display = "USDT" if deposit_method == 'usdt_payment' else "wallet balance"
                    resend.Emails.send({
                        "from": SENDER_EMAIL,
                        "to": seller_info['email'],
                        "subject": f"Deposit Rejected - Order {order_id[:8]}",
                        "html": f"""
                        <h2>Deposit Payment Rejected</h2>
                        <p>Hello {seller_info.get('name', 'Seller')},</p>
                        <p>Unfortunately, your {method_display} deposit payment for Order <strong>{order_id[:8]}</strong> could not be confirmed.</p>
                        <p><strong>Reason:</strong> {req.rejectionReason}</p>
                        <p><strong>Payment Method:</strong> {method_display.title()}</p>
                        {f"<p><strong>Transaction Hash:</strong> {deposit.get('transaction_hash')}</p>" if deposit.get('transaction_hash') else ""}
                        {"<p>Your wallet balance has been restored.</p>" if deposit_method == 'internal_wallet' else "<p>Please verify the transaction details and submit again, or contact support if you believe this is an error.</p>"}
                        """
                    })
            except Exception as e:
                logging.warning(f"Failed to send seller notification: {str(e)}")
            
            return {
                "success": True,
                "message": "Deposit rejected. Seller has been notified.",
                "orderId": order_id,
                "status": "rejected",
                "reason": req.rejectionReason
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Confirm deposit error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@api_router.post("/orders/{order_id}/ship-by-platform")
async def ship_order_by_platform(order_id: str, req: ShipByPlatformRequest, current_user: dict = Depends(get_current_user)):
    """Platform ships the order (admin only)"""
    try:
        user_role = current_user.get('role')
        
        if user_role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # 1. Verify order exists and deposit is received
        order_result = supabase_admin.table('orders')\
            .select('*')\
            .eq('id', order_id)\
            .execute()
        
        if not order_result.data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = order_result.data[0]
        
        if order.get('escrow_status') != 'deposit_received':
            raise HTTPException(status_code=400, detail="Order must have deposit received before shipping")
        
        # 2. Update order status to 'shipped'
        update_data = {
            'escrow_status': 'shipped'
        }
        
        # Note: Only updating escrow_status (orderStatus column doesn't exist in current schema)
        supabase_admin.table('orders')\
            .update(update_data)\
            .eq('id', order_id)\
            .execute()
        
        # 3. Create or update shipment record if needed
        if req.trackingNumber:
            # Check if shipments table exists
            try:
                supabase_admin.table('shipments').upsert({
                    'orderId': order_id,
                    'trackingNumber': req.trackingNumber,
                    'courierName': req.courierName or 'Platform Courier',
                    'courierCode': 'platform',
                    'status': 'shipped',
                    'shippedAt': datetime.now(timezone.utc).isoformat()
                }, on_conflict='orderId').execute()
            except:
                logging.warning("Shipments table may not exist, skipping shipment record")
        
        return {
            "success": True,
            "message": "Order marked as shipped by platform",
            "orderId": order_id,
            "trackingNumber": req.trackingNumber,
            "status": "shipped"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Ship by platform error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/orders/{order_id}/confirm-delivery")
async def confirm_delivery(order_id: str, current_user: dict = Depends(get_current_user)):
    """Buyer confirms delivery and triggers settlement"""
    try:
        user_id = current_user['id']
        user_role = current_user.get('role')
        
        # 1. Verify order exists and is shipped
        order_result = supabase_admin.table('orders')\
            .select('*, order_items(*, store_products(stores(*)))')\
            .eq('id', order_id)\
            .execute()
        
        if not order_result.data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = order_result.data[0]
        
        # Verify buyer owns this order
        if order.get('buyer_id') != user_id:
            raise HTTPException(status_code=403, detail="You can only confirm your own orders")
        
        if order.get('escrow_status') not in ['shipped', 'delivered']:
            raise HTTPException(status_code=400, detail="Order must be shipped before confirming delivery")
        
        # 2. Update order to delivered
        supabase_admin.table('orders')\
            .update({
                'escrow_status': 'delivered',
                'delivery_confirmed_at': datetime.now(timezone.utc).isoformat()
            })\
            .eq('id', order_id)\
            .execute()
        
        # 3. Get all sellers for this order and trigger settlement
        sellers = {}
        for item in order.get('order_items', []):
            store_product = item.get('store_products')
            if store_product:
                store = store_product.get('stores')
                if store:
                    seller_id = store.get('seller_id')
                    if seller_id not in sellers:
                        sellers[seller_id] = 0
                    # Calculate seller's portion (item price * quantity)
                    sellers[seller_id] += float(item.get('price', 0)) * int(item.get('quantity', 1))
        
        # 4. Trigger settlement for each seller
        settlement_results = []
        for seller_id, seller_amount in sellers.items():
            deposit_amount = seller_amount * 0.8  # 80% deposit
            
            try:
                # Call the database function for atomic settlement
                result = supabase_admin.rpc('settle_order_after_delivery', {
                    'p_order_id': order_id,
                    'p_seller_id': seller_id,
                    'p_order_amount': seller_amount,
                    'p_deposit_amount': deposit_amount
                }).execute()
                
                settlement_results.append({
                    'sellerId': seller_id,
                    'success': True,
                    'amount': seller_amount,
                    'deposit': deposit_amount,
                    'profit': seller_amount - deposit_amount
                })
            except Exception as settle_error:
                logging.error(f"Settlement error for seller {seller_id}: {str(settle_error)}")
                settlement_results.append({
                    'sellerId': seller_id,
                    'success': False,
                    'error': str(settle_error)
                })
        
        return {
            "success": True,
            "message": "Delivery confirmed and settlement processed",
            "orderId": order_id,
            "settlements": settlement_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Confirm delivery error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/admin/platform-wallet")
async def get_platform_wallet(current_user: dict = Depends(get_current_user)):
    """Get platform balance (admin only)"""
    try:
        user_role = current_user.get('role')
        
        if user_role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = supabase_admin.table('platform_balance')\
            .select('*')\
            .eq('id', '00000000-0000-0000-0000-000000000001')\
            .execute()
        
        if not result.data:
            return {
                "balance": 0.00,
                "totalReceived": 0.00,
                "totalPaidOut": 0.00
            }
        
        wallet = result.data[0]
        
        return {
            "balance": float(wallet.get('balance', 0)),
            "totalReceived": float(wallet.get('total_received', 0)),
            "totalPaidOut": float(wallet.get('total_paid_out', 0)),
            "updatedAt": wallet.get('updated_at')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get platform wallet error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/seller/deposit-status/{order_id}")
async def get_deposit_status(order_id: str, current_user: dict = Depends(get_current_user)):
    """Get deposit status for a specific order"""
    try:
        user_id = current_user['id']
        
        result = supabase_admin.table('order_deposits')\
            .select('*')\
            .eq('order_id', order_id)\
            .eq('seller_id', user_id)\
            .execute()
        
        if not result.data:
            return {
                "found": False,
                "message": "No deposit required for this order"
            }
        
        deposit = result.data[0]
        
        return {
            "found": True,
            "orderId": deposit.get('order_id'),
            "requiredAmount": float(deposit.get('required_amount', 0)),
            "depositedAmount": float(deposit.get('deposited_amount', 0)),
            "isComplete": deposit.get('is_deposit_complete', False),
            "depositedAt": deposit.get('deposited_at'),
            "createdAt": deposit.get('created_at')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get deposit status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
