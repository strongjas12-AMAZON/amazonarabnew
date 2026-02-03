-- =====================================================
-- Auto-Delivery Feature Migration (OPTIONAL)
-- =====================================================
-- This migration adds the autoDeliveryAt column to orders table
-- to support automatic order completion after 48 hours of shipping
-- =====================================================

-- Add autoDeliveryAt column to orders table
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS autoDeliveryAt TIMESTAMPTZ;

-- Add index for efficient auto-delivery queries
CREATE INDEX IF NOT EXISTS idx_orders_auto_delivery ON orders(autoDeliveryAt) 
WHERE autoDeliveryAt IS NOT NULL AND payment_status != 'completed';

-- Add comment
COMMENT ON COLUMN orders.autoDeliveryAt IS 'Timestamp when order should be auto-confirmed as delivered (48 hours after shipping)';

-- =====================================================
-- Usage:
-- =====================================================
-- When admin ships order:
--   SET autoDeliveryAt = NOW() + INTERVAL '48 hours'
--
-- Cron job checks:
--   SELECT * FROM orders 
--   WHERE autoDeliveryAt < NOW() 
--   AND payment_status != 'completed'
--
-- Then marks those orders as completed automatically
-- =====================================================
