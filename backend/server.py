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
from datetime import datetime, timezone
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
    payoutWallet: Optional[str] = None


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
        'createdAt': product_data.get('created_at')
    }
    if 'users' in product_data and product_data['users']:
        result['users'] = {
            'name': product_data['users'].get('name'),
            'verificationStatus': product_data['users'].get('verificationStatus') or product_data['users'].get('verification_status') or 'unverified'
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
        'createdAt': order_data.get('created_at')
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
async def get_products(category: Optional[str] = None):
    """Get all verified products, optionally filtered by category"""
    try:
        query = supabase_admin.table('products').select('*, users!seller_id(name, verification_status)')
        
        if category:
            query = query.eq('category', category)
        
        products = query.execute()
        
        verified_products = [
            format_product_response(p) 
            for p in products.data 
            if p.get('users') and (p['users'].get('verificationStatus') == 'verified' or p['users'].get('verification_status') == 'verified')
        ]
        
        return {"success": True, "products": verified_products}
    except Exception as e:
        logging.error(f"Get products error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/products/my")
async def get_my_products(current_user: dict = Depends(get_current_user)):
    """Get seller's own products"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can access this")
    
    try:
        products = supabase_admin.table('products').select('*').eq('seller_id', current_user['id']).execute()
        return {"success": True, "products": [format_product_response(p) for p in products.data]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/products")
async def create_product(request: CreateProductRequest, current_user: dict = Depends(get_current_user)):
    """Create new product"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can create products")
    
    if current_user.get('banStatus') in ('banned', 'suspended'):
        raise HTTPException(status_code=403, detail="Your account is restricted. You cannot create products.")
    
    if current_user['verificationStatus'] != 'verified':
        raise HTTPException(status_code=403, detail="Seller must be verified")
    
    try:
        product_data = {
            'id': str(uuid.uuid4()),
            'title': request.title,
            'description': request.description,
            'price': request.price,
            'category': request.category,
            'images': [],
            'seller_id': current_user['id'],
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase_admin.table('products').insert(product_data).execute()
        return {"success": True, "product": format_product_response(result.data[0])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.put("/products/{product_id}")
async def update_product(product_id: str, request: UpdateProductRequest, current_user: dict = Depends(get_current_user)):
    """Update product"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can update products")
    
    if current_user.get('banStatus') in ('banned', 'suspended'):
        raise HTTPException(status_code=403, detail="Your account is restricted. You cannot manage products.")
    
    try:
        product = supabase_admin.table('products').select('*').eq('id', product_id).eq('seller_id', current_user['id']).execute()
        
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
        if request.category is not None:
            update_data['category'] = request.category
        
        result = supabase_admin.table('products').update(update_data).eq('id', product_id).execute()
        return {"success": True, "product": format_product_response(result.data[0])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, current_user: dict = Depends(get_current_user)):
    """Delete product (seller can delete own, admin can delete any)"""
    if current_user['role'] not in ['seller', 'admin']:
        raise HTTPException(status_code=403, detail="Only sellers or admins can delete products")
    
    if current_user.get('banStatus') in ('banned', 'suspended') and current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Your account is restricted. You cannot manage products.")
    
    try:
        if current_user['role'] == 'admin':
            # Admin can delete any product
            product = supabase_admin.table('products').select('*').eq('id', product_id).execute()
        else:
            # Seller can only delete their own products
            product = supabase_admin.table('products').select('*').eq('id', product_id).eq('seller_id', current_user['id']).execute()
        
        if not product.data:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        
        # Check if product has orders
        order_items = supabase_admin.table('order_items').select('id').eq('product_id', product_id).limit(1).execute()
        if order_items.data:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete product with existing orders. Order history must be preserved."
            )
        
        # Delete product images from storage
        try:
            product_images = product.data[0].get('images', [])
            for img_url in product_images:
                if '/products/' in img_url:
                    file_path = img_url.split('/products/')[-1].split('?')[0]
                    supabase_admin.storage.from_('products').remove([file_path])
        except Exception as storage_error:
            logging.warning(f"Could not delete product images from storage: {str(storage_error)}")
        
        supabase_admin.table('products').delete().eq('id', product_id).execute()
        return {"success": True, "message": "Product deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/admin/products")
async def get_all_products_admin(current_user: dict = Depends(get_current_user)):
    """Get all products for admin management"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Try with the join first - use quoted column name for camelCase
        try:
            products = supabase_admin.table('products').select('*, users!seller_id(name, verification_status)').execute()
            return {"success": True, "products": [format_product_response(p) for p in products.data]}
        except Exception as join_error:
            # If join fails, fetch products and users separately
            logging.warning(f"Product join failed, fetching separately: {str(join_error)}")
            products_res = supabase_admin.table('products').select('*').execute()
            products_data = []
            for product in products_res.data:
                # Fetch seller info separately
                try:
                    seller_res = supabase_admin.table('users').select('name, verification_status').eq('id', product.get('seller_id')).single().execute()
                    product['users'] = seller_res.data if seller_res.data else None
                except:
                    product['users'] = None
                products_data.append(format_product_response(product))
            return {"success": True, "products": products_data}
    except Exception as e:
        logging.error(f"Get all products admin error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
        product = supabase_admin.table('products').select('*').eq('id', product_id).eq('seller_id', current_user['id']).execute()
        
        if not product.data:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        
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
    """Remove product image"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can remove images")
    
    try:
        product = supabase_admin.table('products').select('*').eq('id', product_id).eq('seller_id', current_user['id']).execute()
        
        if not product.data:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        
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
        
        order_data = {
            'id': str(uuid.uuid4()),
            'buyer_id': current_user['id'],
            'total_amount': req.totalAmount,
            'payment_method': payment_method,
            'payment_wallet': 'WALLET_BALANCE' if req.useWallet else ADMIN_CRYPTO_WALLET,
            'payment_status': payment_status,
            'confirmed_by_admin': confirmed_by_admin,
            'confirmed_at': datetime.now(timezone.utc).isoformat() if confirmed_by_admin else None,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        order_result = supabase_admin.table('orders').insert(order_data).execute()
        order_id = order_result.data[0]['id']
        
        order_items_list = []
        for item in req.items:
            item_data = {
                'id': str(uuid.uuid4()),
                'order_id': order_id,
                'product_id': item['productId'],
                'quantity': item['quantity'],
                'price': item['price']
            }
            supabase_admin.table('order_items').insert(item_data).execute()
            order_items_list.append(item_data)
        
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
    """Get user's orders"""
    try:
        if current_user['role'] == 'buyer':
            orders = supabase_admin.table('orders').select('*, order_items(*, products(*))').eq('buyer_id', current_user['id']).execute()
        elif current_user['role'] == 'seller':
            orders = supabase_admin.table('orders').select('*, order_items(*, products(*))').execute()
            filtered_orders = []
            for order in orders.data:
                seller_items = [item for item in order['order_items'] if item['products']['seller_id'] == current_user['id']]
                if seller_items:
                    order['order_items'] = seller_items
                    filtered_orders.append(order)
            return {"success": True, "orders": [format_order_response(o) for o in filtered_orders]}
        elif current_user['role'] == 'admin':
            orders = supabase_admin.table('orders').select('*, order_items(*, products(*)), users!buyer_id(name, email)').execute()
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
        # 1) Fetch all completed/paid orders with items & products for this seller
        orders_result = (
            supabase_admin.table("orders")
            .select("*, order_items(*, products(*))")
            .in_("payment_status", ["paid", "completed"])
            .execute()
        )

        total_earnings = 0.0
        for order in orders_result.data or []:
            for item in order.get("order_items", []):
                product = item.get("products") or {}
                if product.get("seller_id") == current_user["id"]:
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
            "payoutWallet": req.payoutWallet,
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
            'payment_status': request.status
        }
        
        if request.status == 'paid':
            update_data['confirmed_by_admin'] = True
            update_data['confirmed_at'] = datetime.now(timezone.utc).isoformat()
        
        result = supabase_admin.table('orders').update(update_data).eq('id', order_id).execute()
        
        # When order is completed, update seller wallets with earnings
        if result.data and request.status == 'completed':
            order_data = result.data[0]
            # Fetch order items with products
            order_items_result = supabase_admin.table('order_items').select('*, products(*)').eq('order_id', order_id).execute()
            
            # Group earnings by seller
            seller_earnings = {}
            for item in (order_items_result.data or []):
                product = item.get('products', {})
                seller_id = product.get('seller_id')
                if seller_id:
                    earnings = float(item.get('price', 0)) * int(item.get('quantity', 0))
                    seller_earnings[seller_id] = seller_earnings.get(seller_id, 0) + earnings
            
            # Update each seller's wallet
            for seller_id, earnings_amount in seller_earnings.items():
                seller_wallet = await get_or_create_seller_wallet(seller_id)
                current_balance = float(seller_wallet.get('balance', 0))
                current_total_earnings = float(seller_wallet.get('totalEarnings') or seller_wallet.get('total_earnings', 0))
                
                new_balance = current_balance + earnings_amount
                new_total_earnings = current_total_earnings + earnings_amount
                
                supabase_admin.table('seller_wallets').update({
                    'balance': new_balance,
                    'totalEarnings': new_total_earnings,
                    'updatedAt': datetime.now(timezone.utc).isoformat()
                }).eq('userId', seller_id).execute()
                
                # Create transaction record
                await create_wallet_transaction(
                    user_id=seller_id,
                    user_role='seller',
                    transaction_type='earning',
                    amount=earnings_amount,
                    previous_balance=current_balance,
                    new_balance=new_balance,
                    order_id=order_id,
                    description=f"Earnings from order: ${earnings_amount:.2f}"
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
