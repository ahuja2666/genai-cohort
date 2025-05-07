document.querySelector('.email-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const emailInput = this.querySelector('input[type="email"]');
    if(emailInput.value) {
        alert(`Thanks for signing up with: ${emailInput.value}`);
        emailInput.value = '';
    }
});
