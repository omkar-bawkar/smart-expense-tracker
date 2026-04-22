// Confirm before adding expense
function confirmAdd() {
    return confirm("Add this expense?");
}

// Simple alert after page loads
window.onload = function () {
    const message = document.getElementById("flash-message");
    if (message) {
        alert(message.innerText);
    }
};
