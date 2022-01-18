function set_img_size() {
    /**
     * Изменение размера картинок с помощью слайдера.
     */
        var rng = document.getElementById('img_size'); 
        var images = document.querySelectorAll(".image")
        images.forEach(img => {
            img.style.width = rng.value + "%";
        });
}

function set_img_count() {
    /**
     * Изменение количества картинок с помощью слайдера
     */
    var images = document.querySelectorAll(".image");
    let percent = document.getElementById('n_images').value;
    var len = images.length;
    var n = Math.round(len * percent / 100);
    var di = Math.round(len / n);
    var i = 1;
    images.forEach(img => {
        if (i % di == 0) {
            img.style.display =  "inline-block";
        } else {
            img.style.display =  "none";
        }
        i += 1;
    });
}


//function tab_changer() {
//    /**
//     * Переключение между слайдерами
//     */
//    let buttons = document.querySelectorAll(".left-bar-btn");
//    let divs = document.querySelectorAll(".tab-content")
//
//    buttons.forEach(function(button) {
//        button.addEventListener("click", function() {
//            let tab_id = button.getAttribute("data-tab");
//            let current_tabs = document.querySelectorAll(tab_id);
//
//
//            buttons.forEach(btn => {
//                btn.classList.remove("active");
//            });
//
//            divs.forEach(div => {
//                div.classList.remove("active");
//            })
//
//            button.classList.add("active");
//
//            current_tabs.forEach(item => {
//                item.classList.add("active");
//            })
//
//
//        });
//    });
//}



//document.addEventListener("DOMContentLoaded", function mainloop() {
////   tab_changer();
//   document.querySelector(".left-bar-btn").click();
//});

