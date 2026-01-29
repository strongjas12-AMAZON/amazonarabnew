import React, { useState } from 'react';
import { Mail, MapPin, Clock, Send, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';
import api from '../lib/api';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setSubmitting(true);
      
      // Create FormData for the API request
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('email', formData.email);
      formDataToSend.append('subject', formData.subject);
      formDataToSend.append('message', formData.message);
      
      // Send to backend API
      const response = await api.post('/contact', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if (response.data.success) {
        setSubmitted(true);
        toast.success('Message sent successfully!');
        
        // Reset form after 5 seconds
        setTimeout(() => {
          setFormData({ name: '', email: '', subject: '', message: '' });
          setSubmitted(false);
        }, 5000);
      }
    } catch (error) {
      console.error('Contact form error:', error);
      toast.error(error.response?.data?.detail || 'Failed to send message. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="font-['Playfair_Display'] text-5xl sm:text-6xl font-bold text-gold-gradient mb-4" data-testid="contact-title">
            Get in Touch
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Have questions about Amazon Arab? We're here to help. Reach out to our support team for assistance with orders, seller verification, or general inquiries.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          {/* Contact Information Cards */}
          <div className="luxury-card text-center" data-testid="contact-email-card">
            <div className="w-16 h-16 bg-gradient-to-br from-[#D4AF37] to-[#F4E4B0] rounded-full mx-auto mb-4 flex items-center justify-center">
              <Mail className="w-8 h-8 text-[#0a0a0a]" />
            </div>
            <h3 className="font-['Playfair_Display'] text-xl font-semibold text-[#D4AF37] mb-2">Email Us</h3>
            <a href="mailto:support@arabshopping.org" className="text-gray-300 hover:text-[#D4AF37] transition-colors">
              support@arabshopping.org
            </a>
            <p className="text-gray-500 text-sm mt-2">We'll respond within 24 hours</p>
          </div>

          <div className="luxury-card text-center" data-testid="contact-location-card">
            <div className="w-16 h-16 bg-gradient-to-br from-[#D4AF37] to-[#F4E4B0] rounded-full mx-auto mb-4 flex items-center justify-center">
              <MapPin className="w-8 h-8 text-[#0a0a0a]" />
            </div>
            <h3 className="font-['Playfair_Display'] text-xl font-semibold text-[#D4AF37] mb-2">Location</h3>
            <p className="text-gray-300">Middle East</p>
            <p className="text-gray-500 text-sm mt-2">Serving customers worldwide</p>
          </div>

          <div className="luxury-card text-center" data-testid="contact-hours-card">
            <div className="w-16 h-16 bg-gradient-to-br from-[#D4AF37] to-[#F4E4B0] rounded-full mx-auto mb-4 flex items-center justify-center">
              <Clock className="w-8 h-8 text-[#0a0a0a]" />
            </div>
            <h3 className="font-['Playfair_Display'] text-xl font-semibold text-[#D4AF37] mb-2">Support Hours</h3>
            <p className="text-gray-300">24/7 Email Support</p>
            <p className="text-gray-500 text-sm mt-2">Round-the-clock assistance</p>
          </div>
        </div>

        {/* Contact Form */}
        <div className="max-w-3xl mx-auto">
          <div className="luxury-card">
            <h2 className="font-['Playfair_Display'] text-3xl font-bold text-white mb-6 text-center">Send Us a Message</h2>
            
            {submitted ? (
              <div className="text-center py-12" data-testid="contact-success-message">
                <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-white mb-2">Message Sent!</h3>
                <p className="text-gray-400">Your email client should open shortly. We'll get back to you soon.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
                      Your Name *
                    </label>
                    <input
                      id="name"
                      name="name"
                      type="text"
                      required
                      value={formData.name}
                      onChange={handleChange}
                      className="luxury-input"
                      placeholder="John Doe"
                      data-testid="contact-name-input"
                    />
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                      Email Address *
                    </label>
                    <input
                      id="email"
                      name="email"
                      type="email"
                      required
                      value={formData.email}
                      onChange={handleChange}
                      className="luxury-input"
                      placeholder="you@example.com"
                      data-testid="contact-email-input"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="subject" className="block text-sm font-medium text-gray-300 mb-2">
                    Subject *
                  </label>
                  <select
                    id="subject"
                    name="subject"
                    required
                    value={formData.subject}
                    onChange={handleChange}
                    className="luxury-input"
                    data-testid="contact-subject-select"
                  >
                    <option value="">Select a subject</option>
                    <option value="General Inquiry">General Inquiry</option>
                    <option value="Order Support">Order Support</option>
                    <option value="Seller Verification">Seller Verification</option>
                    <option value="Payment Issue">Payment Issue</option>
                    <option value="Product Question">Product Question</option>
                    <option value="Technical Support">Technical Support</option>
                    <option value="Partnership Opportunity">Partnership Opportunity</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="message" className="block text-sm font-medium text-gray-300 mb-2">
                    Your Message *
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    required
                    value={formData.message}
                    onChange={handleChange}
                    rows="6"
                    className="luxury-input min-h-[150px]"
                    placeholder="Tell us how we can help you..."
                    data-testid="contact-message-input"
                  />
                </div>

                <button
                  type="submit"
                  className="btn-gold w-full flex items-center justify-center gap-2"
                  data-testid="contact-submit-btn"
                >
                  <Send className="w-5 h-5" />
                  Send Message
                </button>
              </form>
            )}
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mt-20">
          <h2 className="font-['Playfair_Display'] text-4xl font-bold text-center text-gold-gradient mb-12">
            Frequently Asked Questions
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            <div className="luxury-card">
              <h3 className="font-semibold text-[#D4AF37] text-lg mb-3">How do I become a verified seller?</h3>
              <p className="text-gray-400 text-sm">
                Register as a seller, obtain a merchant invite code from our admin team, and upload your business documents for verification. Our team will review and approve within 24-48 hours.
              </p>
            </div>

            <div className="luxury-card">
              <h3 className="font-semibold text-[#D4AF37] text-lg mb-3">What payment methods do you accept?</h3>
              <p className="text-gray-400 text-sm">
                We exclusively accept USDT cryptocurrency on the TRC20 network. All payments are manually verified by our admin team for maximum security.
              </p>
            </div>

            <div className="luxury-card">
              <h3 className="font-semibold text-[#D4AF37] text-lg mb-3">How long does payment verification take?</h3>
              <p className="text-gray-400 text-sm">
                Our admin team reviews and confirms crypto payments within a few hours. Once confirmed, your order status will be updated to "Paid" and processing begins.
              </p>
            </div>

            <div className="luxury-card">
              <h3 className="font-semibold text-[#D4AF37] text-lg mb-3">Can I track my order?</h3>
              <p className="text-gray-400 text-sm">
                Yes! Log into your buyer dashboard to view all your orders and their current status. You'll receive updates as your order progresses through verification and processing.
              </p>
            </div>

            <div className="luxury-card">
              <h3 className="font-semibold text-[#D4AF37] text-lg mb-3">What if I send USDT on the wrong network?</h3>
              <p className="text-gray-400 text-sm">
                IMPORTANT: Only send USDT on TRC20 network. Sending on ERC20 or BEP20 networks will result in permanent loss of funds. Always double-check the network before sending.
              </p>
            </div>

            <div className="luxury-card">
              <h3 className="font-semibold text-[#D4AF37] text-lg mb-3">How do I get a merchant invite code?</h3>
              <p className="text-gray-400 text-sm">
                Contact our support team at support@arabshopping.org with your business details. Approved applicants will receive a unique invite code to complete their seller registration.
              </p>
            </div>
          </div>
        </div>

        {/* Additional Info */}
        <div className="mt-16 luxury-card bg-[rgba(212,175,55,0.05)]">
          <div className="text-center">
            <h3 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-4">
              Need Immediate Assistance?
            </h3>
            <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
              For urgent matters regarding active orders, payment verification, or account issues, please email us directly at support@arabshopping.org with your order ID or account details. Our team monitors this inbox 24/7.
            </p>
            <a
              href="mailto:support@arabshopping.org"
              className="btn-gold inline-flex items-center gap-2"
            >
              <Mail className="w-5 h-5" />
              Email Support Now
            </a>
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div>
            <div className="text-3xl font-bold text-[#D4AF37] mb-2">24/7</div>
            <p className="text-gray-400">Email Support Available</p>
          </div>
          <div>
            <div className="text-3xl font-bold text-[#D4AF37] mb-2">&lt;24h</div>
            <p className="text-gray-400">Average Response Time</p>
          </div>
          <div>
            <div className="text-3xl font-bold text-[#D4AF37] mb-2">100%</div>
            <p className="text-gray-400">Secure Communications</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;
