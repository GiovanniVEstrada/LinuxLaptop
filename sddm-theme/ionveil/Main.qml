import QtQuick 2.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: Screen.width
    height: Screen.height
    color: "#05070b"

    // ── Palette ────────────────────────────────────────────────
    readonly property color colBg:    "#05070b"
    readonly property color colPanel: "#090e18"
    readonly property color colText:  "#f6f8ff"
    readonly property color colMuted: "#aab4c8"
    readonly property color colCyan:  "#6ee7ff"
    readonly property color colPink:  "#ff6bd6"
    readonly property color colGreen: "#95f3c3"

    // ── Clock timer ────────────────────────────────────────────
    Timer {
        interval: 1000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            var now = new Date()
            clockHM.text   = Qt.formatTime(now, "HH:mm")
            clockSec.text  = Qt.formatTime(now, "ss")
            clockDate.text = Qt.formatDate(now, "dddd, MMMM d").toLowerCase()
        }
    }

    // ── Kernel + uptime from /proc ─────────────────────────────
    Component.onCompleted: {
        passwordInput.forceActiveFocus()

        var xk = new XMLHttpRequest()
        xk.open("GET", "file:///proc/version")
        xk.onreadystatechange = function() {
            if (xk.readyState !== XMLHttpRequest.DONE) return
            var m = xk.responseText.match(/Linux version (\S+)/)
            if (m) kernelText.text = m[1]
        }
        xk.send()

        var xu = new XMLHttpRequest()
        xu.open("GET", "file:///proc/uptime")
        xu.onreadystatechange = function() {
            if (xu.readyState !== XMLHttpRequest.DONE) return
            var secs = parseFloat(xu.responseText.split(" ")[0])
            var h = Math.floor(secs / 3600)
            var m = Math.floor((secs % 3600) / 60)
            uptimeText.text = (h < 10 ? "0" : "") + h + ":" + (m < 10 ? "0" : "") + m
        }
        xu.send()
    }

    // ── Background ─────────────────────────────────────────────
    Image {
        anchors.fill: parent
        source: "assets/wallpaper.png"
        fillMode: Image.PreserveAspectCrop
        cache: false
    }

    // ── Top-left: IonVeil branding ─────────────────────────────
    Column {
        anchors { left: parent.left; top: parent.top; margins: 48 }
        spacing: 4

        Row {
            spacing: 14

            Rectangle {
                width: 34; height: 34; radius: 4
                color: Qt.rgba(110/255, 231/255, 255/255, 0.08)
                border.color: root.colCyan; border.width: 1

                Canvas {
                    anchors.centerIn: parent
                    width: 22; height: 22
                    onPaint: {
                        var c = getContext("2d")
                        var cx = width / 2, cy = height / 2
                        c.strokeStyle = "#6ee7ff"; c.lineWidth = 1.2
                        var radii = [9, 5]
                        for (var i = 0; i < radii.length; i++) {
                            c.beginPath(); c.arc(cx, cy, radii[i], 0, 2 * Math.PI); c.stroke()
                        }
                        c.beginPath(); c.moveTo(cx - 11, cy); c.lineTo(cx + 11, cy); c.stroke()
                        c.fillStyle = "#6ee7ff"
                        c.beginPath(); c.arc(cx, cy, 2, 0, 2 * Math.PI); c.fill()
                    }
                }
            }

            Text {
                text: "IonVeil"
                font.pixelSize: 20; font.weight: Font.Bold
                font.family: "JetBrains Mono"
                color: root.colText
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Text {
            text: "tech-noir desktop"
            font.pixelSize: 12; font.family: "JetBrains Mono"
            color: root.colMuted; leftPadding: 48
        }
        Text {
            text: "session  hyprland"
            font.pixelSize: 12; font.family: "JetBrains Mono"
            color: root.colMuted; leftPadding: 48
        }
    }

    // ── Top-right: Clock ───────────────────────────────────────
    Column {
        anchors { right: parent.right; top: parent.top; margins: 48 }
        spacing: 4

        Row {
            anchors.right: parent.right
            Text {
                id: clockHM
                font.pixelSize: 72; font.weight: Font.Light
                font.family: "JetBrains Mono"; color: root.colText
            }
            Text {
                text: ":"
                font.pixelSize: 72; font.weight: Font.Light
                font.family: "JetBrains Mono"; color: root.colCyan; opacity: 0.4
            }
            Text {
                id: clockSec
                font.pixelSize: 72; font.weight: Font.Light
                font.family: "JetBrains Mono"; color: root.colCyan
            }
        }
        Text {
            id: clockDate
            anchors.right: parent.right
            font.pixelSize: 13; font.family: "JetBrains Mono"; color: root.colMuted
        }
    }

    // ── Center: Login card ─────────────────────────────────────
    Rectangle {
        id: card
        width: 400; height: 340
        anchors.centerIn: parent
        radius: 14
        color: Qt.rgba(9/255, 14/255, 24/255, 0.88)
        border.color: Qt.rgba(184/255, 207/255, 255/255, 0.12)
        border.width: 1

        // Corner bracket accents — top-left
        Rectangle { x: -1; y: -1; width: 22; height: 1; color: root.colCyan }
        Rectangle { x: -1; y: -1; width: 1; height: 22; color: root.colCyan }
        // top-right
        Rectangle { x: card.width - 21; y: -1; width: 22; height: 1; color: root.colCyan }
        Rectangle { x: card.width; y: -1; width: 1; height: 22; color: root.colCyan }
        // bottom-left
        Rectangle { x: -1; y: card.height; width: 22; height: 1; color: root.colCyan }
        Rectangle { x: -1; y: card.height - 21; width: 1; height: 22; color: root.colCyan }

        Column {
            anchors { horizontalCenter: parent.horizontalCenter; top: parent.top; topMargin: 36 }
            spacing: 18
            width: parent.width - 64

            // Avatar
            Rectangle {
                width: 84; height: 84; radius: 42
                anchors.horizontalCenter: parent.horizontalCenter
                color: Qt.rgba(110/255, 231/255, 255/255, 0.07)
                border.color: root.colCyan; border.width: 1.5

                Canvas {
                    anchors.centerIn: parent
                    width: 50; height: 50
                    onPaint: {
                        var c = getContext("2d")
                        var cx = width / 2, cy = height / 2
                        c.strokeStyle = "#6ee7ff"; c.lineWidth = 1.5
                        var radii = [21, 14, 7]
                        for (var i = 0; i < radii.length; i++) {
                            c.beginPath(); c.arc(cx, cy, radii[i], 0, 2 * Math.PI); c.stroke()
                        }
                        c.beginPath(); c.moveTo(cx - 23, cy); c.lineTo(cx + 23, cy); c.stroke()
                        c.fillStyle = "#6ee7ff"
                        c.beginPath(); c.arc(cx, cy, 2.5, 0, 2 * Math.PI); c.fill()
                    }
                }
            }

            // Username + subtitle
            Column {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 6

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "gio"
                    font.pixelSize: 22; font.weight: Font.Medium
                    font.family: "JetBrains Mono"; color: root.colText
                }
                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 7
                    Rectangle {
                        width: 7; height: 7; radius: 4; color: root.colGreen
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    Text {
                        text: "authenticated host  ·  arch linux"
                        font.pixelSize: 11; font.family: "JetBrains Mono"; color: root.colMuted
                    }
                }
            }

            // Password field
            Rectangle {
                id: pwField
                width: parent.width; height: 50; radius: 8
                color: Qt.rgba(5/255, 7/255, 11/255, 0.85)
                border.color: passwordInput.activeFocus ? root.colCyan : Qt.rgba(184/255, 207/255, 255/255, 0.18)
                border.width: passwordInput.activeFocus ? 1.5 : 1

                Text {
                    anchors { left: parent.left; verticalCenter: parent.verticalCenter; leftMargin: 16 }
                    text: "🔒"; font.pixelSize: 14; color: root.colMuted
                }

                Text {
                    anchors { left: parent.left; right: submitBtn.left; verticalCenter: parent.verticalCenter; leftMargin: 42; rightMargin: 8 }
                    text: "password"
                    font.pixelSize: 14; font.family: "JetBrains Mono"
                    color: Qt.rgba(170/255, 180/255, 200/255, 0.35)
                    visible: passwordInput.text === "" && !passwordInput.activeFocus
                }

                TextInput {
                    id: passwordInput
                    anchors { left: parent.left; right: submitBtn.left; verticalCenter: parent.verticalCenter; leftMargin: 42; rightMargin: 8 }
                    echoMode: TextInput.Password
                    passwordCharacter: "●"
                    font.pixelSize: 14; font.family: "JetBrains Mono"; color: root.colText
                    focus: true
                    Keys.onReturnPressed: doLogin()
                }

                Rectangle {
                    id: submitBtn
                    width: 36; height: 36; radius: 6
                    anchors { right: parent.right; verticalCenter: parent.verticalCenter; rightMargin: 7 }
                    color: submitHover.containsMouse ? Qt.rgba(110/255, 231/255, 255/255, 0.15) : "transparent"
                    border.color: root.colCyan; border.width: 1

                    Text { anchors.centerIn: parent; text: "→"; font.pixelSize: 17; color: root.colCyan }

                    MouseArea {
                        id: submitHover
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: doLogin()
                    }
                }
            }

            // Hint
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "enter passphrase to lift the veil"
                font.pixelSize: 11; font.family: "JetBrains Mono"
                color: Qt.rgba(170/255, 180/255, 200/255, 0.45)
            }
        }
    }

    // ── Bottom bar ─────────────────────────────────────────────
    Rectangle {
        anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
        height: 44
        color: Qt.rgba(3/255, 5/255, 9/255, 0.82)

        Row {
            anchors { left: parent.left; verticalCenter: parent.verticalCenter; leftMargin: 36 }
            spacing: 0
            Text { text: "layout  "; font.pixelSize: 12; font.family: "JetBrains Mono"; color: root.colMuted }
            Text { text: "us"; font.pixelSize: 12; font.family: "JetBrains Mono"; color: root.colCyan }
            Text { text: "  ·  kernel  "; font.pixelSize: 12; font.family: "JetBrains Mono"; color: root.colMuted }
            Text { id: kernelText; text: "linux"; font.pixelSize: 12; font.family: "JetBrains Mono"; color: root.colText }
            Text { text: "  ·  uptime  "; font.pixelSize: 12; font.family: "JetBrains Mono"; color: root.colMuted }
            Text { id: uptimeText; text: "00:00"; font.pixelSize: 12; font.family: "JetBrains Mono"; color: root.colText }
        }

        Row {
            anchors { right: parent.right; verticalCenter: parent.verticalCenter; rightMargin: 36 }
            spacing: 20

            Row {
                spacing: 7; anchors.verticalCenter: parent.verticalCenter
                Text { text: "net"; font.pixelSize: 12; font.family: "JetBrains Mono"; color: root.colMuted; anchors.verticalCenter: parent.verticalCenter }
                Rectangle { width: 6; height: 6; radius: 3; color: root.colGreen; anchors.verticalCenter: parent.verticalCenter }
                Text { text: "stable"; font.pixelSize: 12; font.family: "JetBrains Mono"; color: root.colMuted; anchors.verticalCenter: parent.verticalCenter }
            }

            Row {
                spacing: 8; anchors.verticalCenter: parent.verticalCenter

                Rectangle {
                    width: 28; height: 28; radius: 4
                    color: suspendHover.containsMouse ? Qt.rgba(110/255, 231/255, 255/255, 0.1) : "transparent"
                    border.color: Qt.rgba(184/255, 207/255, 255/255, 0.22); border.width: 1
                    Text { anchors.centerIn: parent; text: "⏾"; font.pixelSize: 14; color: root.colMuted }
                    MouseArea { id: suspendHover; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: sddm.suspend() }
                }
                Rectangle {
                    width: 28; height: 28; radius: 4
                    color: rebootHover.containsMouse ? Qt.rgba(110/255, 231/255, 255/255, 0.1) : "transparent"
                    border.color: Qt.rgba(184/255, 207/255, 255/255, 0.22); border.width: 1
                    Text { anchors.centerIn: parent; text: "↺"; font.pixelSize: 14; color: root.colMuted }
                    MouseArea { id: rebootHover; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: sddm.reboot() }
                }
                Rectangle {
                    width: 28; height: 28; radius: 4
                    color: powerHover.containsMouse ? Qt.rgba(110/255, 231/255, 255/255, 0.1) : "transparent"
                    border.color: Qt.rgba(184/255, 207/255, 255/255, 0.22); border.width: 1
                    Text { anchors.centerIn: parent; text: "⏻"; font.pixelSize: 14; color: root.colMuted }
                    MouseArea { id: powerHover; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: sddm.powerOff() }
                }
            }
        }
    }

    // ── Login ──────────────────────────────────────────────────
    function doLogin() {
        var session = 0
        for (var i = 0; i < sessionModel.rowCount(); i++) {
            var name = sessionModel.data(sessionModel.index(i, 0), Qt.DisplayRole) || ""
            if (name.toLowerCase().indexOf("hyprland") !== -1) { session = i; break }
        }
        sddm.login("gio", passwordInput.text, session)
        passwordInput.text = ""
    }
}
