// Cart functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add to cart buttons
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const coffeeId = this.dataset.coffeeId;
            const quantity = 1;
            
            addToCart(coffeeId, quantity);
        });
    });
    
    // Quantity controls in cart
    const quantityControls = document.querySelectorAll('.quantity-control');
    quantityControls.forEach(control => {
        const minusBtn = control.querySelector('.quantity-minus');
        const plusBtn = control.querySelector('.quantity-plus');
        const quantityInput = control.querySelector('.quantity-input');
        
        if (minusBtn && plusBtn && quantityInput) {
            minusBtn.addEventListener('click', function() {
                let quantity = parseInt(quantityInput.value);
                if (quantity > 1) {
                    quantity--;
                    quantityInput.value = quantity;
                    updateCartItem(quantityInput.dataset.coffeeId, quantity);
                }
            });
            
            plusBtn.addEventListener('click', function() {
                let quantity = parseInt(quantityInput.value);
                quantity++;
                quantityInput.value = quantity;
                updateCartItem(quantityInput.dataset.coffeeId, quantity);
            });
            
            quantityInput.addEventListener('change', function() {
                updateCartItem(this.dataset.coffeeId, parseInt(this.value));
            });
        }
    });
    
    // Remove from cart buttons
    const removeButtons = document.querySelectorAll('.remove-from-cart');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const coffeeId = this.dataset.coffeeId;
            removeFromCart(coffeeId);
        });
    });
    
    // Flash message auto-hide
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
    
    // Form validation
    const forms = document.querySelectorAll('form[novalidate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                const invalidFields = this.querySelectorAll(':invalid');
                invalidFields.forEach(field => {
                    field.classList.add('is-invalid');
                    
                    // Create error message if not exists
                    let errorMessage = field.parentElement.querySelector('.invalid-feedback');
                    if (!errorMessage) {
                        errorMessage = document.createElement('div');
                        errorMessage.className = 'invalid-feedback';
                        field.parentElement.appendChild(errorMessage);
                    }
                    
                    errorMessage.textContent = field.validationMessage;
                });
            }
            
            this.classList.add('was-validated');
        });
    });
    
    // Remove invalid class when user starts typing
    const formInputs = document.querySelectorAll('.form-control');
    formInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
            const errorMessage = this.parentElement.querySelector('.invalid-feedback');
            if (errorMessage) {
                errorMessage.remove();
            }
        });
    });
});

// API Functions
async function addToCart(coffeeId, quantity) {
    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ coffee_id: coffeeId, quantity: quantity })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update cart count in navbar
            const cartCount = document.querySelector('.cart-count');
            if (cartCount) {
                cartCount.textContent = data.cart_count;
            }
            
            // Show success message
            showNotification(data.message, 'success');
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('Failed to add item to cart', 'error');
    }
}

async function updateCartItem(coffeeId, quantity) {
    try {
        const response = await fetch('/api/cart/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ coffee_id: coffeeId, quantity: quantity })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update cart count and total
            const cartCount = document.querySelector('.cart-count');
            if (cartCount) {
                cartCount.textContent = data.cart_count;
            }
            
            const cartTotal = document.querySelector('.cart-total h3');
            if (cartTotal) {
                cartTotal.textContent = `Total: ${data.total}`;
            }
            
            // If quantity is 0, remove the item from DOM
            if (quantity <= 0) {
                const cartItem = document.querySelector(`[data-coffee-id="${coffeeId}"]`).closest('.cart-item');
                if (cartItem) {
                    cartItem.remove();
                }
            }
        }
    } catch (error) {
        console.error('Error updating cart:', error);
        showNotification('Failed to update cart', 'error');
    }
}

async function removeFromCart(coffeeId) {
    try {
        const response = await fetch(`/api/cart/remove/${coffeeId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update cart count in navbar
            const cartCount = document.querySelector('.cart-count');
            if (cartCount) {
                cartCount.textContent = data.cart_count;
            }
            
            // Remove item from DOM
            const cartItem = document.querySelector(`[data-coffee-id="${coffeeId}"]`).closest('.cart-item');
            if (cartItem) {
                cartItem.remove();
            }
            
            // Show success message
            showNotification(data.message, 'success');
        }
    } catch (error) {
        console.error('Error removing from cart:', error);
        showNotification('Failed to remove item from cart', 'error');
    }
}

// Notification system
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `flash ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Add to flash messages container or create one
    let container = document.querySelector('.flash-messages');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-messages';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .is-invalid {
        border-color: #f44336 !important;
    }
    
    .invalid-feedback {
        color: #f44336;
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
`;
document.head.appendChild(style);