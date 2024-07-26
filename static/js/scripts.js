document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const sidebarToggle = document.getElementById("sidebarToggle");

    sidebarToggle.addEventListener("click", function () {
        sidebar.classList.toggle("hidden");
        sidebarToggle.classList.toggle("active");
    });

    function handleResize() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove("hidden");
            sidebarToggle.classList.remove("active");
            sidebarToggle.style.display = "none";
        } else {
            sidebar.classList.add("hidden");
            sidebarToggle.style.display = "block";
        }
    }

    window.addEventListener("resize", handleResize);
    handleResize(); // 초기 로드 시 사이드바 상태 설정
});

var calendar;
$(document).ready(function () {
    // 내 정보 클릭 시 모달 표시
    $("#profileLink").on("click", function () {
        $("#passwordModal").modal("show");
    });

    // 모달이 완전히 표시된 후에 포커스 설정
    $("#passwordModal").on("shown.bs.modal", function () {
        $("#passwordCheck").focus();
    });

    // 엔터 키 이벤트 처리
    $("#passwordCheck").on("keypress", function (e) {
        if (e.which == 13) {
            checkPassword();
        }
    });

    // 확인 버튼 클릭 시 비밀번호 검증
    $("#passwordCheckButton").on("click", function () {
        checkPassword();
    });

    const sidebarToggle = document.getElementById("sidebarToggle");
    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", toggleSidebar);
    }

    if ($("#calendar").length > 0) {
        var calendarEl = document.getElementById("calendar");
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: "dayGridMonth",
            locale: "ko",
            headerToolbar: {
                left: "prev",
                center: "title today",
                right: "next"
            },
            events: function (fetchInfo, successCallback, failureCallback) {
                var start = fetchInfo.startStr;
                var end = fetchInfo.endStr;
                start = formatDate(new Date(fetchInfo.startStr));
                end = formatDate(new Date(fetchInfo.endStr));

                $.ajax({
                    url: "/get_calendar/" + start + "/" + end,
                    method: "GET",
                    beforeSend: function () {},
                    success: function (data) {
                        var events = data.map(function (item) {
                            returnData = {
                                start: item.date,
                                allDay: true
                            };
                            if (item.type === "<class 'counseling.models.Log'>") {
                                returnData["title"] = "상담 " + item.count + "건";
                                returnData["backgroundColor"] = "#2ec4b6";
                                returnData["borderColor"] = "#2ec4b6";
                                returnData["textColor"] = "black";
                            } else if (item.type === "<class 'education.models.Log'>") {
                                returnData["title"] = "트레이닝 " + item.count + "건";
                                returnData["backgroundColor"] = "#9ec5fe";
                                returnData["borderColor"] = "#9ec5fe";
                                returnData["textColor"] = "black";
                            } else {
                                returnData["title"] = "퀴즈 " + item.count + "건";
                                returnData["backgroundColor"] = "#58b0e3";
                                returnData["borderColor"] = "#58b0e3";
                                returnData["textColor"] = "black";
                            }
                            return returnData;
                        });
                        successCallback(events);
                    },
                    error: function () {
                        failureCallback();
                    },
                    complete: function () {}
                });
            },
            eventClick: function (info) {
                var flag = info.event.title.split(" ")[0];
                var date = new Date(info.event.start);
                date = formatDate(new Date(info.event.start));
                console.log(date);

                if (flag === "상담") {
                    window.location.href = "counseling/history?startDate=" + date + "&endDate=" + date;
                } else if (flag === "퀴즈") {
                    window.location.href = "education/quiz_history?startDate=" + date + "&endDate=" + date;
                } else {
                    window.location.href = "education/edu_history?startDate=" + date + "&endDate=" + date;
                }
            }
        });
        calendar.render();
    }
});

function checkPassword() {
    var password = $("#passwordCheck").val();
    var csrfToken = $("input[name=csrfmiddlewaretoken]").val();

    $.ajax({
        url: "/verify-password/",
        type: "POST",
        data: {
            password: password,
            csrfmiddlewaretoken: csrfToken
        },
        success: function (response) {
            if (response.valid) {
                window.location.href = "/edit_profile/";
            } else {
                $("#passwordCheckError").show();
            }
        }
    });
}

function formatDate(date) {
    var year = date.getFullYear();
    var month = ("0" + (date.getMonth() + 1)).slice(-2);
    var day = ("0" + date.getDate()).slice(-2);

    return year + "-" + month + "-" + day;
}

function openContractPopup() {
    var width = 800;
    var height = 600;
    var left = (screen.width - width) / 2;
    var top = (screen.height - height) / 2;
    window.open("contract/", "Terms and Conditions", "width=" + width + ",height=" + height + ",top=" + top + ",left=" + left);
}

function openPrivacyPopup() {
    var width = 800;
    var height = 600;
    var left = (screen.width - width) / 2;
    var top = (screen.height - height) / 2;
    window.open("privacy/", "Privacy Policy", "width=" + width + ",height=" + height + ",top=" + top + ",left=" + left);
}

function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("hidden");
}
