-- Order Center Database Schema Migration
-- Run this in Supabase SQL Editor

-- ============================================
-- Step 1: Add order_status column to orders table
-- ============================================

-- Add order_status column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'orders' AND column_name = 'order_status'
    ) THEN
        ALTER TABLE orders ADD COLUMN order_status TEXT DEFAULT 'pending_payment';
    END IF;
END $$;

-- Add seller_id column to orders if not exists (for direct seller reference)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'orders' AND column_name = 'seller_id'
    ) THEN
        ALTER TABLE orders ADD COLUMN seller_id UUID REFERENCES users(id);
    END IF;
END $$;

-- Add constraint for order_status values
DO $$
BEGIN
    -- Drop existing constraint if exists
    ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_order_status_check;
    
    -- Add new constraint with all status values
    ALTER TABLE orders ADD CONSTRAINT orders_order_status_check 
        CHECK (order_status IN (
            'pending_payment', 
            'to_be_shipped', 
            'to_be_received', 
            'to_be_evaluated', 
            'completed',
            'after_sales',
            'cancelled',
            'refund_completed'
        ));
EXCEPTION WHEN OTHERS THEN
    -- Constraint might fail if data exists with invalid values
    RAISE NOTICE 'Could not add order_status constraint: %', SQLERRM;
END $$;

-- ============================================
-- Step 2: Create shipments table
-- ============================================

CREATE TABLE IF NOT EXISTS shipments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    tracking_number TEXT,
    courier_name TEXT,
    courier_code TEXT,
    shipped_at TIMESTAMP WITH TIME ZONE,
    estimated_delivery TIMESTAMP WITH TIME ZONE,
    delivery_status TEXT DEFAULT 'pending' CHECK (delivery_status IN (
        'pending', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'failed'
    )),
    delivery_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_shipments_order_id ON shipments(order_id);
CREATE INDEX IF NOT EXISTS idx_shipments_tracking ON shipments(tracking_number);

-- ============================================
-- Step 3: Create refunds table
-- ============================================

CREATE TABLE IF NOT EXISTS refunds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    buyer_id UUID NOT NULL REFERENCES users(id),
    seller_id UUID REFERENCES users(id),
    refund_type TEXT DEFAULT 'refund' CHECK (refund_type IN ('refund', 'return', 'exchange')),
    reason TEXT NOT NULL,
    description TEXT,
    evidence_urls TEXT[] DEFAULT '{}',
    requested_amount DECIMAL(10,2),
    approved_amount DECIMAL(10,2),
    status TEXT DEFAULT 'pending' CHECK (status IN (
        'pending', 'seller_review', 'approved', 'rejected', 'processing', 'completed', 'cancelled'
    )),
    seller_response TEXT,
    seller_responded_at TIMESTAMP WITH TIME ZONE,
    admin_note TEXT,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for refunds
CREATE INDEX IF NOT EXISTS idx_refunds_order_id ON refunds(order_id);
CREATE INDEX IF NOT EXISTS idx_refunds_buyer_id ON refunds(buyer_id);
CREATE INDEX IF NOT EXISTS idx_refunds_seller_id ON refunds(seller_id);
CREATE INDEX IF NOT EXISTS idx_refunds_status ON refunds(status);

-- ============================================
-- Step 4: Create order_reviews table (for evaluations)
-- ============================================

CREATE TABLE IF NOT EXISTS order_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    buyer_id UUID NOT NULL REFERENCES users(id),
    seller_id UUID REFERENCES users(id),
    product_id UUID REFERENCES products(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_images TEXT[] DEFAULT '{}',
    is_anonymous BOOLEAN DEFAULT false,
    seller_reply TEXT,
    seller_replied_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(order_id, buyer_id, product_id)
);

-- Create indexes for reviews
CREATE INDEX IF NOT EXISTS idx_reviews_order_id ON order_reviews(order_id);
CREATE INDEX IF NOT EXISTS idx_reviews_seller_id ON order_reviews(seller_id);
CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON order_reviews(product_id);

-- ============================================
-- Step 5: Enable RLS on new tables
-- ============================================

ALTER TABLE shipments ENABLE ROW LEVEL SECURITY;
ALTER TABLE refunds ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_reviews ENABLE ROW LEVEL SECURITY;

-- ============================================
-- Step 6: RLS Policies for shipments
-- ============================================

-- Sellers can view shipments for their orders
CREATE POLICY "shipments_seller_select" ON shipments
FOR SELECT TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM orders o
        WHERE o.id = shipments.order_id
        AND o.seller_id = auth.uid()
    )
);

-- Sellers can insert shipments for their orders
CREATE POLICY "shipments_seller_insert" ON shipments
FOR INSERT TO authenticated
WITH CHECK (
    EXISTS (
        SELECT 1 FROM orders o
        WHERE o.id = shipments.order_id
        AND o.seller_id = auth.uid()
    )
);

-- Sellers can update their shipments
CREATE POLICY "shipments_seller_update" ON shipments
FOR UPDATE TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM orders o
        WHERE o.id = shipments.order_id
        AND o.seller_id = auth.uid()
    )
);

-- Buyers can view shipments for their orders
CREATE POLICY "shipments_buyer_select" ON shipments
FOR SELECT TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM orders o
        WHERE o.id = shipments.order_id
        AND o."buyerId" = auth.uid()
    )
);

-- ============================================
-- Step 7: RLS Policies for refunds
-- ============================================

-- Sellers can view refunds for their orders
CREATE POLICY "refunds_seller_select" ON refunds
FOR SELECT TO authenticated
USING (seller_id = auth.uid());

-- Sellers can update refunds (respond/approve/reject)
CREATE POLICY "refunds_seller_update" ON refunds
FOR UPDATE TO authenticated
USING (seller_id = auth.uid());

-- Buyers can view their own refund requests
CREATE POLICY "refunds_buyer_select" ON refunds
FOR SELECT TO authenticated
USING (buyer_id = auth.uid());

-- Buyers can create refund requests
CREATE POLICY "refunds_buyer_insert" ON refunds
FOR INSERT TO authenticated
WITH CHECK (buyer_id = auth.uid());

-- ============================================
-- Step 8: RLS Policies for order_reviews
-- ============================================

-- Anyone can view reviews (public)
CREATE POLICY "reviews_public_select" ON order_reviews
FOR SELECT TO authenticated, anon
USING (true);

-- Buyers can create reviews for their orders
CREATE POLICY "reviews_buyer_insert" ON order_reviews
FOR INSERT TO authenticated
WITH CHECK (buyer_id = auth.uid());

-- Sellers can update reviews (to reply)
CREATE POLICY "reviews_seller_update" ON order_reviews
FOR UPDATE TO authenticated
USING (seller_id = auth.uid());

-- ============================================
-- Step 9: Update orders RLS to include seller access
-- ============================================

-- Drop existing policy if exists and recreate
DROP POLICY IF EXISTS "orders_seller_select" ON orders;

-- Sellers can view orders where they are the seller
CREATE POLICY "orders_seller_select" ON orders
FOR SELECT TO authenticated
USING (seller_id = auth.uid());

-- Sellers can update their orders (for status changes)
DROP POLICY IF EXISTS "orders_seller_update" ON orders;
CREATE POLICY "orders_seller_update" ON orders
FOR UPDATE TO authenticated
USING (seller_id = auth.uid());

-- ============================================
-- Step 10: Create function to update order seller_id from order_items
-- ============================================

-- Function to set seller_id on orders based on the first order item's product seller
CREATE OR REPLACE FUNCTION update_order_seller_id()
RETURNS TRIGGER AS $$
BEGIN
    -- Get seller_id from the product in order_items
    UPDATE orders
    SET seller_id = (
        SELECT p.seller_id 
        FROM order_items oi
        JOIN seller_products sp ON sp.product_id = oi."productId"
        WHERE oi."orderId" = NEW."orderId"
        LIMIT 1
    )
    WHERE id = NEW."orderId" AND seller_id IS NULL;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-populate seller_id
DROP TRIGGER IF EXISTS trigger_update_order_seller ON order_items;
CREATE TRIGGER trigger_update_order_seller
AFTER INSERT ON order_items
FOR EACH ROW
EXECUTE FUNCTION update_order_seller_id();

-- ============================================
-- Step 11: Enable Realtime for order-related tables
-- ============================================

-- Enable realtime publication for orders
ALTER PUBLICATION supabase_realtime ADD TABLE orders;
ALTER PUBLICATION supabase_realtime ADD TABLE shipments;
ALTER PUBLICATION supabase_realtime ADD TABLE refunds;

-- ============================================
-- Done! Schema migration complete.
-- ============================================
