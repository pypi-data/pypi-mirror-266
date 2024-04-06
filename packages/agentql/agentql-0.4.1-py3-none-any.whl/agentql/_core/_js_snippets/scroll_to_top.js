async () => {
    const viewportHeight = window.document.documentElement.clientHeight;
    let scrolledHeight = window.scrollY; 

    while (scrolledHeight > 0) {
        scrolledHeight -= viewportHeight;
        if (scrolledHeight < 0) {
            scrolledHeight = 0;
        }
        window.scrollTo({ top: scrolledHeight, left: 0, behavior: 'smooth' });
        timeout = Math.floor(Math.random() * (100 - 50 + 1)) + 50;
        await new Promise(resolve => setTimeout(resolve, timeout));
    }
}
