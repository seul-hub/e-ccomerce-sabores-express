document.addEventListener("DOMContentLoaded", () => {
    const imagen = document.getElementById("imagen-login");
    const caja = document.querySelector(".login-box");

    // Si la persona tiene activado "reducir movimiento" en su sistema, no se anima nada
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        return;
    }

    if (imagen) {
        // Entra deslizándose desde la izquierda
        imagen.animate(
            [
                { opacity: 0, transform: "translateX(-40px)" },
                { opacity: 1, transform: "translateX(0)" }
            ],
            { duration: 800, easing: "ease-out", fill: "backwards" }
        );

        // Después "respira" suavemente, sin parar
        imagen.animate(
            [
                { transform: "scale(1)" },
                { transform: "scale(1.03)" }
            ],
            {
                duration: 3000,
                delay: 800,
                easing: "ease-in-out",
                iterations: Infinity,
                direction: "alternate"
            }
        );
    }

    if (caja) {
        // La tarjeta del formulario sube con un fundido
        caja.animate(
            [
                { opacity: 0, transform: "translateY(30px)" },
                { opacity: 1, transform: "translateY(0)" }
            ],
            { duration: 700, delay: 300, easing: "ease-out", fill: "backwards" }
        );
    }
});