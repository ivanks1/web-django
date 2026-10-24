"use strict"

document.querySelectorAll(".autoExpand").forEach((input) => {
    const resize = () => {
        input.style.width = "0px"
        input.style.width = `${Math.max(160, input.scrollWidth + 2)}px`
    }
    input.addEventListener("input", resize)
    resize();
})

document.getElementById("preview-resume").addEventListener("click", () => {
    const preview = document.getElementById("resume-preview")
    preview.querySelectorAll("[data-preview]").forEach((output) => {
        const input = document.querySelector(`[name="${output.dataset.preview}"]`)
        output.textContent = input.value
    })
    preview.hidden = false
})

// плавная прокрутка к секциям
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
})