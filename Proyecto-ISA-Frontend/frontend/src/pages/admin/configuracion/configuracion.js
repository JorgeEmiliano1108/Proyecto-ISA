document.addEventListener('DOMContentLoaded', () => {
    const picker = document.getElementById('colorPicker');
    const colorValue = document.getElementById('colorValue');
    const colorPreview = document.getElementById('colorPreview');

    const savedColor = localStorage.getItem('isaThemeColor');
    if (savedColor) {
        document.documentElement.style.setProperty('--primary-color', savedColor);
        picker.value = savedColor;
        colorValue.textContent = savedColor;
        colorPreview.style.backgroundColor = savedColor;
    } else {
        colorPreview.style.backgroundColor = picker.value;
    }

    picker.addEventListener('input', (e) => {
        const color = e.target.value;
        document.documentElement.style.setProperty('--primary-color', color);
        localStorage.setItem('isaThemeColor', color);
        colorValue.textContent = color;
        colorPreview.style.backgroundColor = color;
    });
});
