function sign_in() {
  let username = $("#input-username").val();
  let password = $("#input-password").val();

  if (!username || !password) {
    alert("Mohon lengkapi username dan password.");
    return;
  }
  $.ajax({
    type: "POST",
    url: "/login_save",
    data: {
      username_give: username,
      password_give: password,
    },
    success: function (response) {
      if (response["result"] === "success") {
        let token = response["token"];
        $.cookie("mytoken", token, { path: "/" });
        alert("Login Berhasil!");
        window.location.href = "/adminpanel";
      } else {
        alert(response["msg"]);
      }
    },
  });
}

function sign_out() {
  $.removeCookie("mytoken", { path: "/" });
  alert("Anda telah keluar");
  window.location.href = "/login";
}

function posting() {
  let title = $("#input-title").val().trim();
  let file = $("#input-file").prop("files")[0];
  let layout = $("#layout-select").val(); // Ambil nilai dropdown

  if (!title || !file || !layout) {
    alert("Mohon lengkapi data dengan benar");
    return;
  }

  // Validasi tipe file (hanya menerima gambar)
  if (!file.type.startsWith("image/") || file.type === "image/gif") {
    alert("Mohon pilih file gambar!");
    return;
  }

  // Validasi kapasitas file (maksimum 2 megabyte)
  if (file.size > 2 * 1024 * 1024) {
    alert("Ukuran file terlalu besar, maksimum 2 megabyte diperbolehkan");
    return;
  }

  // Membuat objek formData
  let form_data = new FormData();
  form_data.append("title_give", title);
  form_data.append("file_give", file);
  form_data.append("layout_give", layout); // Menambahkan nilai layout ke formData

  $.ajax({
    type: "POST",
    url: "/adminpanel/posting",
    data: form_data,
    contentType: false,
    processData: false,
    success: function (response) {
      alert(response["msg"]);
      window.location.reload();
    },
  });
}

function listing() {
  $.ajax({
    type: "GET",
    url: "/get-posts",
    data: {},
    success: function (response) {
      let card = response["card"];
      for (let i = 0; i < card.length; i++) {
        let title = card[i]["title"];
        let file = card[i]["file"];
        let num = card[i]["num"];
        let layout = card[i]["layout"];
        let temp_html = `
          <tr>
          <th scope="row">${i + 1}</th>
          <td>${title}</td>
          <td>
            <img
              src="../${file}"
              class="img-fluid data-foto"
            />
          </td>
          <td>${layout}</td>
          <td>
            <a href="/adminpanel/posting/${num}" class="btn btn-success">
              <i class="bi bi-search"></i>          
            </a>
            <button class="btn btn-danger" onclick="deletePost('${num}')">
              <i class="bi bi-trash3-fill"></i>
            </button>
          </td>
        </tr>
        `;
        $("#cards-box").append(temp_html);
      }
    },
  });
}

function deletePost(num) {
  $.ajax({
    type: "POST",
    url: "/adminpanel/delete-post",
    data: { num_give: num },
    success: function (response) {
      alert(response["msg"]);
      window.location.reload();
    },
  });
}

function gallery() {
  $.ajax({
    type: "GET",
    url: "/get_posts",
    data: {},
    success: function (response) {
      let card = response["card"];
      let currentRowHtml = '<div class="row">'; // Mulai dengan satu baris baru
      let currentColCount = 0; // Menghitung jumlah kolom dalam baris saat ini

      for (let i = 0; i < card.length; i++) {
        let file = card[i]["file"];
        let colSize = card[i]["layout"] || 12; // Default menjadi 6 jika colSize tidak ada
        let temp_html = `
          <div class="col-md-${colSize} mb-4 aos-init aos-animate" data-aos="flip-down">
            <a href="/">
              <div>
                <img class="img-fluid" src="../${file}" alt="" height="100%">
              </div>
            </a>
          </div>
        `;

        // Tambahkan elemen kolom ke `currentRowHtml` dan tambahkan jumlah kolom saat ini
        currentRowHtml += temp_html;
        currentColCount += colSize;

        // Cek apakah total kolom melebihi 12
        if (currentColCount >= 12) {
          // Jika total kolom melebihi 12, tambahkan `currentRowHtml` ke `#cards-box` dan reset `currentRowHtml` dan jumlah kolom
          currentRowHtml += "</div>"; // Tutup baris saat ini
          $("#cards-box").append(currentRowHtml);
          currentRowHtml = '<div class="row">'; // Mulai dengan baris baru
          currentColCount = 0; // Reset jumlah kolom
        }
      }

      // Pastikan untuk menambahkan baris terakhir jika belum mencapai 12 kolom
      if (currentColCount > 0) {
        currentRowHtml += "</div>"; // Tutup baris saat ini
        $("#cards-box").append(currentRowHtml);
      }
    },
  });
}

function detail_post(num) {
  $.ajax({
    type: "GET",
    url: `/adminpanel/posting/${num}`, // Menggunakan URL yang sesuai dengan rute Flask yang baru
    success: function (response) {
      if (response.result === "success") {
      } else {
        alert("Gagal mengambil detail posting!");
      }
    },
  });
}
