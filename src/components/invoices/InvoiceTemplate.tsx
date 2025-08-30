import React from 'react';
import { Invoice } from '../../types';
import './InvoiceTemplate.css';

interface InvoiceTemplateProps {
  invoice: Invoice;
  onPrint?: () => void;
  onClose?: () => void;
}

const InvoiceTemplate: React.FC<InvoiceTemplateProps> = ({ invoice, onPrint, onClose }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(amount);
  };

  return (
    <div className="invoice-template">
      {/* Print Button */}
      <div className="print-controls mb-3">
        <button onClick={onPrint} className="btn btn-primary me-2">
          <i className="fas fa-print me-2"></i>Print Invoice
        </button>
        {onClose && (
          <button onClick={onClose} className="btn btn-secondary">
            <i className="fas fa-times me-2"></i>Close
          </button>
        )}
      </div>

      {/* A4 Invoice Container */}
      <div className="invoice-a4" id="invoice-to-print">
        {/* Header */}
        <div className="invoice-header">
          <div className="business-info">
            <h1 className="business-name">{invoice.business_name}</h1>
            <p className="business-address">{invoice.business_address}</p>
            <p className="business-phone">Phone: {invoice.business_phone}</p>
          </div>
          <div className="invoice-details">
            <h2 className="invoice-title">INVOICE</h2>
            <div className="invoice-meta">
              <div className="meta-item">
                <strong>Invoice #:</strong> {invoice.invoice_number}
              </div>
              <div className="meta-item">
                <strong>Date:</strong> {formatDate(invoice.invoice_date)}
              </div>
            </div>
          </div>
        </div>

        {/* Customer Information */}
        <div className="customer-section">
          <h3>Bill To:</h3>
          <div className="customer-info">
            <p className="customer-name"><strong>{invoice.customer_name}</strong></p>
            <p className="customer-address">{invoice.customer_address}</p>
            <p className="customer-phone">Phone: {invoice.customer_phone}</p>
          </div>
        </div>

        {/* Items Table */}
        <div className="items-section">
          <table className="invoice-table">
            <thead>
              <tr>
                <th className="col-sno">S.No</th>
                <th className="col-product">Product</th>
                <th className="col-description">Description</th>
                <th className="col-qty">Qty</th>
                <th className="col-price">Unit Price</th>
                <th className="col-total">Total</th>
              </tr>
            </thead>
            <tbody>
              {invoice.items?.map((item, index) => (
                <tr key={item.id}>
                  <td className="text-center">{index + 1}</td>
                  <td className="product-name">{item.product?.name || 'Unknown Product'}</td>
                  <td className="product-description">{item.product?.description || ''}</td>
                  <td className="text-center">{item.quantity}</td>
                  <td className="text-end">{formatCurrency(item.unit_price)}</td>
                  <td className="text-end">{formatCurrency(item.total)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="total-row">
                <td colSpan={5} className="text-end"><strong>Total:</strong></td>
                <td className="text-end"><strong>{formatCurrency(invoice.total_amount)}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>

        {/* Custom Columns */}
        {invoice.custom_columns && Object.keys(invoice.custom_columns).length > 0 && (
          <div className="custom-columns-section">
            <h3>Additional Information:</h3>
            <table className="custom-table">
              <tbody>
                {Object.entries(invoice.custom_columns).map(([key, value]) => (
                  <tr key={key}>
                    <td className="custom-label"><strong>{key}:</strong></td>
                    <td className="custom-value">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Notes */}
        {invoice.notes && (
          <div className="notes-section">
            <h3>Notes:</h3>
            <p className="notes-text">{invoice.notes}</p>
          </div>
        )}

        {/* Footer */}
        <div className="invoice-footer">
          <div className="footer-content">
            <p>Thank you for your business!</p>
            <p className="footer-note">
              This is a computer generated invoice. No signature required.
            </p>
          </div>
        </div>
             </div>
     </div>
   );
 };

export default InvoiceTemplate;
