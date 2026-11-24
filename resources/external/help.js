// Copy buttons of the example programs.
(function () {
    function fallbackCopy(text) {
        const area = document.createElement("textarea");
        area.value = text;
        area.style.position = "fixed";
        area.style.opacity = "0";
        document.body.appendChild(area);
        area.select();
        const copied = document.execCommand("copy");
        document.body.removeChild(area);
        return copied;
    }

    function confirm(button, copied) {
        const label = button.dataset.label || button.textContent;
        button.dataset.label = label;
        button.textContent = copied ? (button.dataset.done || "Copied") : (button.dataset.failed || "Select and copy");
        button.classList.toggle("done", copied);
        setTimeout(function () {
            button.textContent = label;
            button.classList.remove("done");
        }, 1500);
    }

    document.addEventListener("click", function (event) {
        const button = event.target.closest(".copy");
        if (!button) {
            return;
        }
        const text = button.closest(".example").querySelector("pre").innerText.replace(/\s+$/, "") + "\n";
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(
                function () { confirm(button, true); },
                function () { confirm(button, fallbackCopy(text)); }
            );
        } else {
            confirm(button, fallbackCopy(text));
        }
    });
})();
