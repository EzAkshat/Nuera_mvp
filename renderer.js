export function onAuthSuccess(callback) {
    window.electronAPI.onAuthSuccess(callback);
  }
  
  export function onAuthError(callback) {
    window.electronAPI.onAuthError(callback);
  }
  
  export function initLoginPage() {
    const signInBtn = document.getElementById("sign-in-btn");
    const createAccountBtn = document.getElementById("create-account-btn");
  
    if (signInBtn) {
      signInBtn.addEventListener("click", () => {
        window.electronAPI.openExternal(
          "http://localhost:3000/login?redirect_uri=nuera%3A%2F%2Fauth-complete"
        );
      });
    }
  
    if (createAccountBtn) {
      createAccountBtn.addEventListener("click", () => {
        window.electronAPI.openExternal(
          "http://localhost:3000/register?redirect_uri=nuera%3A%2F%2Fauth-complete"
        );
      });
    }
  }
  
  // Set up authentication listeners and initialize the login page
  window.addEventListener('DOMContentLoaded', () => {
    onAuthSuccess((token) => {
      console.log('Authentication successful, token:', token);
      localStorage.setItem('authToken', token);
      loadPage('listening'); // Note: Ensure loadPage is defined or implemented
    });
  
    onAuthError((error) => {
      console.error('Authentication error:', error);
    });
  
    initLoginPage(); // Call initLoginPage to set up button listeners
  });