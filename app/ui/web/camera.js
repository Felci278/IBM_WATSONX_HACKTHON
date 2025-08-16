const video = document.getElementById("video");
const captureBtn = document.getElementById("captureBtn");
const viewBtn = document.getElementById("viewBtn");
const wardrobeSection = document.getElementById("wardrobe");
const wardrobeList = document.getElementById("wardrobeList");
const canvas = document.createElement("canvas");

// Start webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => { video.srcObject = stream; })
    .catch(err => {
        console.error("Error accessing camera:", err);
        alert("Camera access is required.");
    });

// Capture + upload
captureBtn.addEventListener("click", () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        const filename = `capture_${Date.now()}.jpg`;
        formData.append("file", blob, filename);

        try {
            const res = await fetch("/api/closet/ingest", {
                method: "POST",
                body: formData
            });
            const data = await res.json();

            if (res.ok) {
                alert(`✅ Added: ${data.metadata.type} (${data.metadata.color})`);
                loadWardrobe();
            } else {
                alert("❌ Error: " + data.detail);
            }
        } catch (err) {
            console.error(err);
            alert("❌ Upload failed.");
        }
    }, "image/jpeg");
});

// Load wardrobe items
async function loadWardrobe() {
    try {
        const res = await fetch("/api/closet/");
        const data = await res.json();
        wardrobeList.innerHTML = "";

        if (data.items.length === 0) {
            wardrobeList.innerHTML = "<li>No items yet</li>";
        } else {
            data.items.forEach(item => {
                const li = document.createElement("li");
                li.innerHTML = `
                    <div>
                        <strong>${item.type}</strong> 
                        <span class="meta">(${item.color}, ${item.material})</span>
                    </div>
                    <button class="btn small danger" onclick="deleteItem(${item.id})">🗑️ Delete</button>
                `;
                wardrobeList.appendChild(li);
            });
        }

        wardrobeSection.classList.remove("hidden");
    } catch (err) {
        console.error("Failed to load wardrobe:", err);
    }
}

// Delete wardrobe item
async function deleteItem(itemId) {
    if (!confirm("Are you sure you want to delete this item?")) return;

    try {
        const res = await fetch(`/api/closet/${itemId}`, { method: "DELETE" });
        const data = await res.json();

        if (res.ok) {
            alert(`✅ Deleted item ID ${itemId}`);
            loadWardrobe();
        } else {
            alert("❌ Error: " + data.detail);
        }
    } catch (err) {
        console.error("Delete failed:", err);
        alert("❌ Could not delete item.");
    }
}

// Show wardrobe on button click
viewBtn.addEventListener("click", loadWardrobe);
