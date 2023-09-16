function sign_in() {
  let username = $("#input-username").val();
  let password = $("#input-password").val();

  //kode validasi

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
