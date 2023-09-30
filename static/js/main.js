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

  // Membuat objek gambar untuk memeriksa ukuran
  let image = new Image();
  image.src = URL.createObjectURL(file);

  image.onload = function () {
    // Validasi ukuran width dan height
    if (image.width >= 1200 && image.height >= 500) {
      // Gambar memenuhi syarat, lanjutkan dengan pengiriman data
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
    } else {
      alert("Ukuran gambar harus minimal 1200px lebar dan 500px tinggi");
    }
  };

  image.onerror = function () {
    alert(
      "Gagal memuat gambar. Pastikan file yang dipilih adalah gambar yang valid."
    );
  };
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
              src="../static/${file}"
              class="img-fluid data-foto"
            />
          </td>
          <td>${layout}</td>
          <td>
            <a href="/adminpanel/posting/${num}" class="btn btn-success">
              <i class="bi bi-search"></i>          
            </a>
            <button
              type="button"
              class="btn btn-warning"
              data-bs-toggle="modal"
              data-bs-target="#editdataDetail"
              onclick="updatePost('${num}')">
              <i class="bi bi-pencil-square"></i>
            </button>
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

function updatePost(num) {
  $.ajax({
    type: "GET",
    url: `/adminpanel/get-posting/${num}`,
    success: function (response) {
      if (response.result === "success") {
        let post = response.post;
        $("#input-title-edit").val(post.title);
        $("#layout-select-edit").val(post.layout);

        // Set nomor posting pada tombol "Simpan Perubahan"
        $("#update-post-button").attr("onclick", `saveChanges(${num})`);

        // Munculkan modal edit
        $("#editdataDetail").modal("show");
      } else {
        alert(response.msg);
      }
    },
  });
}

function saveChanges(num) {
  let title = $("#input-title-edit").val();
  let newImage = $("#input-file-edit")[0].files[0];
  let layout = $("#layout-select-edit").val();

  let formData = new FormData();
  formData.append("title", title);
  formData.append("layout", layout);

  if (newImage) {
    formData.append("file_give", newImage);
  }

  $.ajax({
    type: "POST",
    url: `/adminpanel/update-posting/${num}`,
    data: formData,
    contentType: false,
    processData: false,
    success: function (response) {
      if (response.result === "success") {
        window.location.reload();
      } else {
        alert(response.msg);
      }
    },
  });
}

function deletePost(num) {
  var confirmDelete = confirm("Apakah Anda yakin ingin menghapus posting ini?");

  if (confirmDelete) {
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
}

function gallery() {
  $.ajax({
    type: "GET",
    url: "/get-posts",
    data: {},
    success: function (response) {
      let card = response["card"];
      for (let i = 0; i < card.length; i++) {
        let file = card[i]["file"];
        let colSize = card[i]["layout"] || 12; // Default menjadi 6 jika colSize tidak ada
        let title = card[i]["title"];
        let temp_html = `
          <div class="col-md-${colSize} mb-4 aos-init aos-animate" data-aos="flip-down">
          <a href="/gallery/2/detail-${title}">
            <div class="img-area">
              <img class="img-fluid photo-img" src="../static/${file}">
            </div>
          </a>
        </div>        
        `;
        $("#cards-box").append(temp_html);
      }
    },
  });
}

function detail_post(num) {
  $.ajax({
    type: "GET",
    url: `/adminpanel/posting/${num}`, // Menggunakan URL yang sesuai dengan rute Flask yang baru
    success: function (response) {},
  });
}

function detail_posting(num) {
  let title = $("#input-title-detail").val().trim();
  let file = $("#input-file-detail").prop("files")[0];
  let layout = $("#layout-select-detail").val(); // Ambil nilai dropdown

  if (!file || !layout || !title) {
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

  // Membuat objek gambar untuk memeriksa ukuran
  let image = new Image();
  image.src = URL.createObjectURL(file);

  image.onload = function () {
    // Validasi ukuran width dan height
    if (image.width >= 1200 && image.height >= 500) {
      // Gambar memenuhi syarat, lanjutkan dengan pengiriman data
      let form_data = new FormData();
      form_data.append("title_give", title);
      form_data.append("file_give", file);
      form_data.append("layout_give", layout); // Menambahkan nilai layout ke formData

      $.ajax({
        type: "POST",
        url: `/adminpanel/posting/${num}`,
        data: form_data,
        contentType: false,
        processData: false,
        success: function (response) {
          alert(response["msg"]);
          window.location.reload();
        },
      });
    } else {
      alert("Ukuran gambar harus minimal 1200px lebar dan 500px tinggi");
    }
  };

  image.onerror = function () {
    alert(
      "Gagal memuat gambar. Pastikan file yang dipilih adalah gambar yang valid."
    );
  };
}

function deletePost_detail(num) {
  if (confirm("Apakah Anda yakin ingin menghapus foto detail ini?")) {
    $.ajax({
      type: "POST",
      url: "/adminpanel/delete-post-detail/" + num, // Sesuaikan dengan URL endpoint Anda
      success: function (response) {
        if (response.result === "success") {
          // Hapus baris tabel dari DOM jika berhasil
          $(`tr[data-num="${num}"]`).remove();
          alert(response.msg); // Tampilkan pesan sukses
          window.location.reload();
        } else {
          alert(response.msg); // Tampilkan pesan error
        }
      },
      error: function () {
        alert("Terjadi kesalahan saat menghapus foto detail.");
      },
    });
  }
}

function gallery_detail(title) {
  $.ajax({
    type: "GET",
    url: `/gallery/2/detail-${title}`,
    success: function (response) {},
  });
}

function sign_up() {
  let username = $("#Username_reg").val().trim();
  let password = $("#password_reg").val();
  let password2 = $("#password2_reg").val();

  let helpUsername = $("#help-username");
  let helpPassword = $("#help-password");
  let helpPassword2 = $("#help-password2");

  if (!username || !password || !password2) {
    alert("Mohon isi data dengan lengkap");
    return;
  }
  // Periksa apakah username sudah digunakan
  $.ajax({
    type: "POST",
    url: "/check-username",
    data: {
      username_check: username,
    },
    success: function (response) {
      if (response.exists) {
        helpUsername
          .text("Username sudah digunakan. Silakan pilih username lain!")
          .addClass("text-danger")
          .removeClass("text-success");
        return;
      } else {
        helpUsername
          .removeClass("text-danger")
          .text("username tersedia")
          .addClass("text-success");
        //kode validation password
        if (!is_password(password)) {
          helpPassword
            .text(
              "Untuk kata sandi Anda, masukkan 8-20 karakter bahasa, angka, atau karakter khusus berikut (!@#$%^&*)"
            )
            .addClass("text-danger")
            .removeClass("text-success");
          return;
        } else {
          helpPassword
            .text("password tersedia")
            .removeClass("text-danger")
            .addClass("text-success");

          if (password2 !== password) {
            helpPassword2
              .text("kata sandi anda tidak cocok")
              .addClass("text-danger");
            return;
          } else {
            helpPassword2.text("").removeClass("text-danger");
          }
        }
        // akhir validation
        $.ajax({
          type: "POST",
          url: "/register-save",
          data: {
            username_give: username,
            password_give: password,
          },
          success: function (response) {
            alert("User baru telah ditambahkan");
            window.location.replace("/adminpanel/register");
          },
        });
      }
    },
  });
}

function is_nickname(asValue) {
  var regExp = /^(?=.*[a-zA-Z])[-a-zA-Z0-9_.]{2,10}$/;
  return regExp.test(asValue);
}

function is_password(asValue) {
  var regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;
  return regExp.test(asValue);
}

function post_users() {
  $.ajax({
    type: "GET",
    url: "/get-users",
    data: {},
    success: function (response) {
      let account = response["account"];
      for (let i = 0; i < account.length; i++) {
        let username = account[i]["username"];
        let num = account[i]["num"];
        let temp_html = `
          <tr>
          <th scope="row">${i + 1}</th>
          <td>${username}</td>
          <td>
            <button class="btn btn-danger" onclick="delete_users(${num})">
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

function delete_users(num) {
  var confirmDelete = confirm("Apakah Anda yakin ingin menghapus user ini?");

  if (confirmDelete) {
    $.ajax({
      type: "POST",
      url: "/delete-users",
      data: { num_give: num },
      success: function (response) {
        alert(response["msg"]);
        window.location.reload();
      },
    });
  }
}
