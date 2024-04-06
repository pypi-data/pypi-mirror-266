async () => {
    const viewportHeight = window.document.documentElement.clientHeight;
    const totalHeight = window.document.documentElement.scrollHeight;
    let scrolledHeight = window.scrollY;

    while (scrolledHeight < totalHeight) {
        scrolledHeight += viewportHeight;
        window.scrollTo({ top: scrolledHeight, left: 0, behavior: 'smooth' });
        timeout = Math.floor(Math.random() * (100 - 50 + 1)) + 50;
        await new Promise(resolve => setTimeout(resolve, timeout));
    }
}
