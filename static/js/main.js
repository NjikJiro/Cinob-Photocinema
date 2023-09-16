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

  if (!title || !file) {
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

  // membuat objek formData
  form_data = new FormData();

  form_data.append("title_give", title);
  form_data.append("file_give", file);

  $.ajax({
    type: "POST",
    url: "/posting",
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
    url: "/get_posts",
    data: {},
    success: function (response) {
      let card = response["card"];
      for (let i = 0; i < card.length; i++) {
        let title = card[i]["title"];
        let file = card[i]["file"];
        let num = card[i]["num"];
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
          <td>
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
    url: "/adminpanel/delete_post",
    data: { num_give: num },
    success: function (response) {
      alert(response["msg"]);
      window.location.reload();
    },
  });
}
