document
  .getElementById("upload-image")
  .addEventListener("change", function (event) {
    let formData = new FormData();
    formData.append("image", event.target.files[0]);

    // Gửi yêu cầu upload ảnh lên server
    fetch("/upload", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          console.error("Error:", data.error);
        } else {
          // Cập nhật ảnh preview
          document.getElementById("image").src = data.file_path;
          document.getElementById("original-image").src = data.file_path;
          document.getElementById("image").dataset.filePath = data.file_path;

          // Xóa ảnh đã xử lý cũ
          document.getElementById("processed-image").src = ""; // Làm trống ảnh đã xử lý

          // Xóa thanh kéo cũ nếu có
          let existingSlider = document.querySelector(".comparison-slider");
          if (existingSlider) {
            existingSlider.remove();
          }

          // Reset vị trí thanh kéo và chiều rộng của ảnh đã xử lý
          let comparisonResize = document.querySelector(".comparison-resize");
          if (comparisonResize) {
            comparisonResize.style.width = "50%"; // Đặt lại width về 50%
          }

          // Tạo lại thanh kéo mới
          initComparison();
        }
      })
      .catch((error) => console.error("Error:", error));
  });

function addNoise(type) {
  processImage(type + "_noise");
}

function denoise(type) {
  processImage("denoise_" + type);
}

function sharpenImage(type) {
  processImage("sharpen_" + type);
}

function detectEdge(type) {
  processImage("edge_" + type);
}

function processImage(processType) {
  let imagePath = document.getElementById("image").dataset.filePath;

  // Gửi yêu cầu xử lý ảnh lên server
  fetch("/process", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      process_type: processType,
      image_path: imagePath,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Response data:", data); // Kiểm tra toàn bộ phản hồi
      if (data.error) {
        console.error("Error:", data.error);
      } else {
        console.log("Processed image path:", data.processed_image_path); // Kiểm tra đường dẫn
        document.getElementById("processed-image").src =
          data.processed_image_path + "?t=" + new Date().getTime();
      }
    })
    .catch((error) => console.error("Error:", error));
}

window.onload = function () {
  initComparison();
};

function initComparison() {
  let slider = document.querySelector(".comparison-slider"); // Lấy thanh kéo đã tồn tại
  if (!slider) {
    slider = document.createElement("div");
    slider.classList.add("comparison-slider");

    let container = document.querySelector(".comparison-container");
    container.appendChild(slider);
  }

  let container = document.querySelector(".comparison-container");
  let comparisonResize = document.querySelector(".comparison-resize");

  let isDragging = false;

  slider.addEventListener("mousedown", (e) => {
    isDragging = true;
  });

  document.addEventListener("mouseup", () => {
    isDragging = false;
  });

  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;

    // Lấy tọa độ của container
    let rect = container.getBoundingClientRect();

    // Lấy vị trí x của chuột trong container
    let x = e.clientX - rect.left;

    // Đảm bảo thanh kéo không vượt ra ngoài vùng ảnh
    if (x < 0) {
      x = 0;
    } else if (x > rect.width) {
      x = rect.width - 5;
    }

    // Cập nhật độ rộng của phần hình ảnh xử lý và vị trí của thanh kéo
    comparisonResize.style.width = x + "px";
    slider.style.left = x + "px";
  });
}

function downloadImage() {
  let filePath = document.getElementById("image").src.split("/").pop();
  window.location.href = "/download/" + filePath;
}
