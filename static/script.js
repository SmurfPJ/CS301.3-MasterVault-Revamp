// Define global interval variable for the countdown
let timerInterval = null;

document.addEventListener('DOMContentLoaded', function() {
  // Define all the UI elements
  const lockSwitch = document.getElementById('lockSwitch');
  const lockRange = document.getElementById('lockRange');
  const lockRangeLabel = document.getElementById('lockRangeLabel');
  const unlockForm = document.getElementById('unlockForm');
  const toggleLockBtn = document.getElementById('toggleLockBtn');
  const masterPasswordInput = document.getElementById('masterPasswordInput');
  const toggleLockVisibilityBtn = document.getElementById('toggleLockVisibilityBtn');
  const toggleLockVisibilityIcon = document.getElementById('toggleLockVisibilityIcon');

  // Initialize the lock range label and button disabled state
  updateRangeLabel();
  lockRange.addEventListener('input', updateRangeLabel);

  // Check lock state from the server when the page loads
  fetch('/check_lock')
    .then(response => response.json())
    .then(data => {
      if (data.locked) {
        const unlockTime = new Date(data.unlock_time);
        const remainingTime = unlockTime - new Date();
        if (remainingTime > 0) {
          startCountdown(remainingTime);
          lockSwitch.checked = true;
          lockRange.disabled = true;
          toggleLockBtn.disabled = false;
          toggleLockBtn.textContent = 'UNLOCK ACCOUNT';
        } else {
          resetLockUI();
        }
      } else {
        resetLockUI();
      }
    })
    .catch(error => console.error('Error:', error));

  // Event listener for the lock switch
  lockSwitch.addEventListener('change', function() {
    lockRange.disabled = !this.checked;
    toggleLockBtn.disabled = !this.checked;
    if (!this.checked) {
      toggleLockBtn.textContent = 'LOCK ACCOUNT';
      unlockForm.style.display = 'none';
      if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
      }
    }
  });

  // Event listener for the lock/unlock button
  toggleLockBtn.addEventListener('click', function() {
    if (this.textContent.trim() === 'LOCK ACCOUNT') {
      const lockDuration = lockRange.value * 10; // Convert to minutes
      lockAccount(lockDuration);
    } else {
      // Attempt to unlock the account
      unlockForm.style.display = unlockForm.style.display === 'none' ? 'block' : 'none';
      this.textContent = unlockForm.style.display === 'block' ? 'CANCEL UNLOCK' : 'LOCK ACCOUNT';
    }
  });

  // Event listener for unlocking the account
  masterPasswordInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      unlockAccount();
    }
  });

  // Event listener for the toggle visibility button
  toggleLockVisibilityBtn.addEventListener('click', function() {
    const type = masterPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    masterPasswordInput.setAttribute('type', type);
    toggleLockVisibilityIcon.classList.toggle('bi-eye-slash');
    toggleLockVisibilityIcon.classList.toggle('bi-eye');
  });
});

function updateRangeLabel() {
  const rangeValue = lockRange.value;
  lockRangeLabel.innerText = rangeValue * 10 + ' minutes'; // Assuming each step of the slider is 10 minutes
}

function lockAccount(duration) {
  fetch('/lock_account', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lockDuration: duration })
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      alert('Account Locked Successfully');

      const unlockTime = new Date(data.unlock_time);
      const remainingTime = unlockTime - new Date();
      
      // Start the countdown
      startCountdown(remainingTime);
      toggleLockBtn.textContent = 'UNLOCK ACCOUNT';
      lockSwitch.disabled = true;
      lockRange.disabled = true;
    } else {
      alert(data.message);
    }
  })
  .catch(error => console.error('Error:', error));
}

function unlockAccount() {
  const masterPassword = masterPasswordInput.value;
  fetch('/unlock_account', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ master_password: masterPassword })
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      alert('Account Unlocked Successfully');

      // Stop the countdown timer
      stopCountdown();

      // Reset the UI
      resetLockUI();
    } else {
      alert('Failed to unlock account: ' + data.message);
    }
  })
  .catch(error => console.error('Error:', error));
}

function stopCountdown() {
  clearInterval(timerInterval);
  timerInterval = null;
  lockRangeLabel.innerText = '0 minutes';
}

function startCountdown(durationInMilliseconds) {
  const endTime = Date.now() + durationInMilliseconds;
  timerInterval = setInterval(() => {
    const remainingTime = endTime - Date.now();
    if (remainingTime <= 0) {
      clearInterval(timerInterval);
      resetLockUI();
    } else {
      const minutes = Math.floor(remainingTime / 60000);
      const seconds = Math.floor((remainingTime % 60000) / 1000);
      lockRangeLabel.innerText = `${minutes}:${seconds.toString().padStart(2, '0')} minutes left`;
    }
  }, 1000);
}

function resetLockUI() {
  const lockSwitch = document.getElementById('lockSwitch');
  const lockRange = document.getElementById('lockRange');
  const lockRangeLabel = document.getElementById('lockRangeLabel');
  const toggleLockBtn = document.getElementById('toggleLockBtn');
  const unlockForm = document.getElementById('unlockForm');

  lockSwitch.checked = false;
  lockSwitch.disabled = false;
  lockRange.value = 0;
  lockRange.disabled = true;
  updateRangeLabel();
  toggleLockBtn.textContent = 'LOCK ACCOUNT';
  toggleLockBtn.disabled = true;
  unlockForm.style.display = 'none';
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}





//2FA Authentications
document.addEventListener('DOMContentLoaded', function() {
    const twoStepVerificationCheckbox = document.getElementById('twoStepVerification');
    const twoStepVerificationInput = document.getElementById('twoStepVerificationInput');
    const verifyPinBtn = document.getElementById('verifyPinBtn');
    const feedbackElement = document.getElementById('twoStepFeedback');
    const userEmailElement = document.getElementById('userEmail');
    const userEmail = userEmailElement ? userEmailElement.textContent : '';

    // Update the 2FA toggle state based on server response
    update2FAToggle();


    twoStepVerificationCheckbox.addEventListener('change', function() {
        if (this.checked) {
            enable2FAandRequestPIN(userEmail, feedbackElement, twoStepVerificationInput);
        } else {
            disable2FA(userEmail, feedbackElement, twoStepVerificationInput);
        }
    });

    verifyPinBtn.addEventListener('click', function() {
        verifyPIN(userEmail, feedbackElement, twoStepVerificationInput);
    });
});


function enable2FAandRequestPIN(userEmail, feedbackElement, twoStepVerificationInput) {
    fetch('/enable_2fa', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email: userEmail })
    })
    .then(response => response.json())
    .then(data => {
        feedbackElement.innerText = data.message;
        requestPIN(userEmail, feedbackElement, twoStepVerificationInput);
    })
    .catch(error => {
        feedbackElement.innerText = 'Error: ' + error.message;
    });
}

function disable2FA(userEmail, feedbackElement, twoStepVerificationInput) {
    fetch('/disable_2fa', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email: userEmail })
    })
    .then(response => response.json())
    .then(data => {
        displayMessageAndHide(feedbackElement, data.message);
        twoStepVerificationInput.style.display = 'none';
    })
    .catch(error => {
        displayMessageAndHide(feedbackElement, 'Error: ' + error.message);
    });
}

function requestPIN(userEmail, feedbackElement, twoStepVerificationInput) {
    fetch('/setup_2fa', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email: userEmail })
    })
    .then(response => response.json())
    .then(data => {
        feedbackElement.innerText = data.message;
        twoStepVerificationInput.style.display = 'block';
    })
    .catch(error => {
        feedbackElement.innerText = 'Error: ' + error.message;
        twoStepVerificationInput.style.display = 'none';
    });
}

function verifyPIN(userEmail, feedbackElement, twoStepVerificationInput) {
    const pin = document.getElementById('twoStepPin').value;
    const verifyPinBtn = document.getElementById('verifyPinBtn'); // Get the verify button
    if (!pin || pin.length !== 4) {
        displayMessageAndHide(feedbackElement, 'Please enter a valid 4-digit PIN.');
        return;
    }

    fetch('/verify_2fa', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email: userEmail, pin: pin })
    })
    .then(response => response.json())
    .then(data => {
        displayMessageAndHide(feedbackElement, data.message);
        if (data.message === '2FA verification successful!') {
            // Hide the PIN input, verify button, and their container upon successful verification
            document.getElementById('twoStepPin').style.display = 'none';
            verifyPinBtn.style.display = 'none';
            twoStepVerificationInput.style.display = 'none';
        }
    })
    .catch(error => {
        displayMessageAndHide(feedbackElement, 'Error verifying PIN: ' + error.message);
    });
}


function displayMessageAndHide(feedbackElement, message, delay = 3500) {
    feedbackElement.innerText = message;
    setTimeout(() => {
        feedbackElement.innerText = '';
    }, delay);
}

function update2FAToggle() {
    fetch('/get_2fa_status')
    .then(response => response.json())
    .then(data => {
        if (data['2fa_enabled'] !== undefined) {
            document.getElementById('twoStepVerification').checked = data['2fa_enabled'];
        }
    })
    .catch(error => console.error('Error fetching 2FA status:', error));
}






document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 3000); // 3s before starting the fade out
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    form.addEventListener("submit", function(event) {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        if (!email || !password) {
            alert("Email and password are required!");
            event.preventDefault();
        }
    });

    // Check the initial password strength
    var initialPassword = document.getElementById('generated-password').value;
    if (initialPassword) {
        checkPasswordStrength(initialPassword);
    }
});

document.getElementById('generated-password').addEventListener('input', function() {
    var password = document.getElementById('generated-password').value;
    var strength = checkPasswordStrength(password);
    updateStrengthIndicator(strength);
});


//login & signup password toggle button//
function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password');
    const togglePasswordIcon = document.getElementById('togglePasswordIcon');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        togglePasswordIcon.className = 'bi bi-eye-slash';
    } else {
        passwordInput.type = 'password';
        togglePasswordIcon.className = 'bi bi-eye';
    }
}

function toggleConfirmPasswordVisibility() {
    const confirmPasswordInput = document.getElementById('confirm_password');
    const toggleConfirmPasswordIcon = document.getElementById('toggleConfirmPasswordIcon');
    if (confirmPasswordInput.type === 'password') {
        confirmPasswordInput.type = 'text';
        toggleConfirmPasswordIcon.className = 'bi bi-eye-slash';
    } else {
        confirmPasswordInput.type = 'password';
        toggleConfirmPasswordIcon.className = 'bi bi-eye';
    }
}

function checkPasswordMatch() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const passwordMatchMessage = document.getElementById('passwordMatchMessage');

    if (password === confirmPassword) {
        passwordMatchMessage.style.color = 'green';
        passwordMatchMessage.innerText = 'Passwords match';
    } else {
        passwordMatchMessage.style.color = 'red';
        passwordMatchMessage.innerText = 'Passwords do not match';
    }
}


//master password toggle//
function toggleMasterPasswordVisibility() {
    const passwordInput = document.getElementById('master_password');
    const togglePasswordIcon = document.getElementById('toggleMasterPasswordIcon');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        togglePasswordIcon.className = 'bi bi-eye-slash';
    } else {
        passwordInput.type = 'password';
        togglePasswordIcon.className = 'bi bi-eye';
    }
}


function toggleConfirmMasterPasswordVisibility() {
    const confirmMasterPasswordInput = document.getElementById('confirmMaster_password');
    const toggleConfirmMasterPasswordIcon = document.getElementById('toggleConfirmMasterPasswordIcon');
    if (confirmMasterPasswordInput.type === 'password') {
        confirmMasterPasswordInput.type = 'text';
        toggleConfirmMasterPasswordIcon.className = 'bi bi-eye-slash';
    } else {
        confirmMasterPasswordInput.type = 'password';
        toggleConfirmMasterPasswordIcon.className = 'bi bi-eye';
    }
}

function checkMasterPasswordMatch() {
    const masterPassword = document.getElementById('master_password').value;
    const confirmMasterPassword = document.getElementById('confirmMaster_password').value;
    const passwordMatchMessage = document.getElementById('passwordMatchMessage');

    if (masterPassword === confirmMasterPassword) {
        passwordMatchMessage.style.color = 'green';
        passwordMatchMessage.innerText = 'Passwords match';
    } else {
        passwordMatchMessage.style.color = 'red';
        passwordMatchMessage.innerText = 'Passwords do not match';
    }
}





//generate passwords
function validateForm() {
    var useNumbers = document.getElementById('numbers').checked;
    var useSymbols = document.getElementById('symbols').checked;

    if (!useNumbers && !useSymbols) {
        alert("Please select at least one option: Include Numbers or Include Symbols.");
        return false;
    }
    return true;
}




function generatePassword(keyword, length, useNumbers, useSymbols) {
    var characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" + keyword;

    if (useNumbers) {
        characters += "0123456789";
    }
    if (useSymbols) {
        characters += "!@#$%^&*()_-+=<>?/[]{}|";
    }

    var password = "";
    for (var i = 0; i < length; i++) {
        // Every third character is from the keyword
        if (i % 3 === 0 && i/3 < keyword.length) {
            password += keyword.charAt(i/3);
        } else {
            password += characters.charAt(Math.floor(Math.random() * characters.length));
        }
    }

    return password;
}


function updateStrengthIndicator(strength) {
    document.getElementById('strength-bar-inner').style.width = (strength.score * 25) + '%';
    document.getElementById('strength-bar-inner').style.backgroundColor = strength.color;
    document.getElementById('strength-text').innerText = strength.status;
}

function refreshPassword() {
    var keyword = document.getElementById('keyword-input').value;
    var length = document.getElementById('length-input').value;
    var useNumbers = document.getElementById('numbers').checked;
    var useSymbols = document.getElementById('symbols').checked;

    var newPassword = generatePassword(keyword, length, useNumbers, useSymbols);
    document.getElementById('generated-password').value = newPassword;

    // Update the password strength checker
    checkPasswordStrength(newPassword);
}


function checkPasswordStrength(password) {
    var strength = {status: 'Weak', score: 0, color: 'red'};

    if (password.length >= 8) strength.score += 1;
    if (/[0-9]/.test(password)) strength.score += 1;
    if (/[A-Z]/.test(password)) strength.score += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength.score += 1;

    if (strength.score === 4) {
        strength.status = 'Very Strong';
        strength.color = 'green';
    } else if (strength.score === 3) {
        strength.status = 'Strong';
        strength.color = 'lightgreen';
    } else if (strength.score === 2) {
        strength.status = 'Moderate';
        strength.color = 'orange';
    }

    // Update the UI with the calculated strength
    updateStrengthIndicator(strength);
}


function copyToClipboard() {
    // Copy password to clipboard
    var passwordField = document.getElementById('generated-password');
    passwordField.select();
    document.execCommand('copy');

    // Change icon to clipboard-check
    document.getElementById('clipboard-icon').className = 'bi bi-clipboard-check';


    setTimeout(function () {
        document.getElementById('clipboard-icon').className = 'bi bi-clipboard';
    }, 2000); //2 seconds
}

function copyWebsite() {
    var field = document.getElementById('website-input');
    field.select();
    document.execCommand('copy');
    changeIconTemporarily('website-icon');
}

function copyEmail() {
    var field = document.getElementById('email-input');
    field.select();
    document.execCommand('copy');
    changeIconTemporarily('email-icon');
}

function copyPassword() {
    var field = document.getElementById('password-input');
    field.select();
    document.execCommand('copy');
    changeIconTemporarily('password-icon');
}

function changeIconTemporarily(iconId) {
    var icon = document.getElementById(iconId);
    icon.className = 'bi bi-clipboard-check';

    setTimeout(function () {
        icon.className = 'bi bi-clipboard';
    }, 2000); // Reset icon after 2 seconds
}

function toggleNewPasswordVisibility() {
    const passwordInput = document.getElementById('newPassword');
    const togglePasswordIcon = document.getElementById('toggleNewPasswordIcon');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        togglePasswordIcon.className = 'bi bi-eye-slash';
    } else {
        passwordInput.type = 'password';
        togglePasswordIcon.className = 'bi bi-eye';
    }
}

function toggleConfirmNewPasswordVisibility() {
    const passwordInput = document.getElementById('confirmNewPassword');
    const togglePasswordIcon = document.getElementById('toggleConfirmNewPasswordIcon');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        togglePasswordIcon.className = 'bi bi-eye-slash';
    } else {
        passwordInput.type = 'password';
        togglePasswordIcon.className = 'bi bi-eye';
    }
}



function checkNewPasswordMatch() {
    const masterPassword = document.getElementById('newPassword').value;
    const confirmMasterPassword = document.getElementById('confirmNewPassword').value;
    const passwordMatchMessage = document.getElementById('passwordMatchMessage');

    if (masterPassword === confirmMasterPassword) {
        passwordMatchMessage.style.color = 'green';
        passwordMatchMessage.innerText = 'Passwords match';
    } else {
        passwordMatchMessage.style.color = 'red';
        passwordMatchMessage.innerText = 'Passwords do not match';
    }
}

//passwordList
function deleteEntry(website, email, password) {
    if (confirm('Are you sure you want to delete this entry?')) {
        fetch('/delete-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({website: website, email: email, password: password})
        }).then(response => {
            if (response.ok) {
                alert('Entry deleted successfully');
                window.location.reload();
            } else {
                alert('Failed to delete entry');
            }
        });
    }
}

//animal ID
function toggleSubmitButton() {
            const submitButton = document.getElementById('submit-button');
            const radioButtons = document.querySelectorAll('input[name="animal"]');
            let isChecked = false;
            radioButtons.forEach((radio) => {
                if (radio.checked) {
                    isChecked = true;
                }
            });
            submitButton.disabled = !isChecked;
        }

function toggleSecurityCheckButton() {
        const checkBox = document.getElementById('securityCheck');
        const submitButton = document.getElementById('confirmButton');
        submitButton.disabled = !checkBox.checked;
    }

document.addEventListener('DOMContentLoaded', function() {
    var img = document.querySelector('.animal-img');
    if (img) {
        img.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    }
});


