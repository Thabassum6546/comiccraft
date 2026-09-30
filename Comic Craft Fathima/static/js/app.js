async function downloadComic(pdfPath) {
    const button = event?.currentTarget;
    if (button) {
        button.disabled = true;
        button.textContent = "Preparing PDF...";
    }

    try {
        const response = await fetch(pdfPath);
        if (!response.ok) throw new Error("PDF download failed.");

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;

        const filename = pdfPath.split("/").pop() || "comic.pdf";
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);

        window.location.href = `/export-success?filename=${encodeURIComponent(filename)}`;
    } catch (error) {
        alert(error.message);
        if (button) {
            button.disabled = false;
            button.textContent = "📄 Download Your Comic as PDF";
        }
    }
}
