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
    """Convert snake_case DB fields to camelCase for frontend"""
    return {
        'id': user_data.get('id'),
        'email': user_data.get('email'),
        'name': user_data.get('name'),
        'role': user_data.get('role'),
        'verificationStatus': user_data.get('verification_status'),
        'createdAt': user_data.get('created_at')
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
            'verificationStatus': product_data['users'].get('verification_status')
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
        result['order_items'] = []
        for item in order_data['order_items']:
            formatted_item = {
                'id': item.get('id'),
                'orderId': item.get('order_id'),
                'productId': item.get('product_id'),
                'quantity': item.get('quantity'),
                'price': item.get('price')
            }
            if 'products' in item and item['products']:
                formatted_item['products'] = format_product_response(item['products'])
            result['order_items'].append(formatted_item)
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
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        
        response = supabase.auth.get_user(token)
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_data = supabase_admin.table('users').select('*').eq('id', response.user.id).execute()
        
        if not user_data.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return format_user_response(user_data.data[0])
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
            'verification_status': 'verified',
            'created_at': datetime.now(timezone.utc).isoformat()
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
                'verification_status': 'verified'  # Pre-verified for testing
            },
            {
                'email': 'testbuyer@test.com', 
                'name': 'Test Buyer',
                'role': 'buyer',
                'verification_status': 'unverified'
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
                'verification_status': test_user['verification_status'],
                'created_at': datetime.now(timezone.utc).isoformat()
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
            'verification_status': 'unverified',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
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
        
        user_data = supabase_admin.table('users').select('*').eq('id', auth_response.user.id).execute()
        
        if not user_data.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "user": format_user_response(user_data.data[0]),
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
            if p.get('users') and p['users'].get('verification_status') == 'verified'
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
    """Delete product"""
    if current_user['role'] != 'seller':
        raise HTTPException(status_code=403, detail="Only sellers can delete products")
    
    try:
        product = supabase_admin.table('products').select('*').eq('id', product_id).eq('seller_id', current_user['id']).execute()
        
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
    
    try:
        order_data = {
            'id': str(uuid.uuid4()),
            'buyer_id': current_user['id'],
            'total_amount': req.totalAmount,
            'payment_method': 'USDT_TRON',
            'payment_wallet': ADMIN_CRYPTO_WALLET,
            'payment_status': 'pending_payment',
            'confirmed_by_admin': False,
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
        
        # Send email notifications (non-blocking)
        asyncio.create_task(send_order_notifications(order_data, order_items_list, "order_placed"))
        
        return {"success": True, "order": format_order_response(order_result.data[0])}
    except Exception as e:
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


@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, request: UpdateOrderStatusRequest, current_user: dict = Depends(get_current_user)):
    """Update order status (admin only)"""
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


# Admin Routes
@api_router.get("/admin/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        users = supabase_admin.table('users').select('*').execute()
        return {"success": True, "users": [format_user_response(u) for u in users.data]}
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
