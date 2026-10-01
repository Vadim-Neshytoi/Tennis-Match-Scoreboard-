// JavaScript for toggling the dropdown menu
document.addEventListener("DOMContentLoaded", function () {
    const navToggle = document.querySelector(".nav-toggle");
    const navLinks = document.querySelector(".nav-links");

    navToggle.addEventListener("click", function () {
        navLinks.classList.toggle("active");
    });

    const notification = document.getElementById("validation-notification");

    if (!notification) {
        return;
    }

    const closeButton = notification.querySelector(
        ".validation-notification-close"
    );

    const hideNotification = function () {
        notification.classList.add("validation-notification-hidden");
    };

    closeButton.addEventListener("click", hideNotification);

    setTimeout(hideNotification, 5000);
});
