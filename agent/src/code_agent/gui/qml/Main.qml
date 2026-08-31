import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import CodeAgent 1.0

ApplicationWindow {
    id: window
    visible: true
    width: 1040
    height: 700
    minimumWidth: 780
    minimumHeight: 540
    title: "Code Agent"
    color: pageBg
    font.family: "Microsoft YaHei"
    property bool showExecution: false

    readonly property color pageBg: "#f6f7f9"
    readonly property color mainBg: "#fbfbfc"
    readonly property color sidebarBg: "#f7f8fa"
    readonly property color panelBg: "#ffffff"
    readonly property color hoverBg: "#f1f3f6"
    readonly property color selectedBg: "#e9ecf3"
    readonly property color selectedBorder: "#cfd6e6"
    readonly property color line: "#e6e8ec"
    readonly property color border: "#dfe3ea"
    readonly property color fg: "#202124"
    readonly property color titleFg: "#111827"
    readonly property color muted: "#6b7280"
    readonly property color faint: "#8b93a1"
    readonly property color accent: "#3946a3"
    readonly property color success: "#16845b"
    readonly property color warning: "#b56d12"
    readonly property color danger: "#c73d50"

    function statusColor(value, kind) {
        if (value === "Error" || kind === "error") return danger
        if (value === "Success" || kind === "finish") return success
        if (value === "Running" || value === "Stopping") return warning
        return faint
    }

    function statusText(value, kind) {
        if (value === "Error" || kind === "error") return "Error"
        if (value === "Success" || kind === "finish") return "Success"
        if (value === "Running" || value === "Stopping") return "Running"
        return ""
    }

    function normalizedEvent(event) {
        event = event || {}
        return {
            kind: String(event.kind || "event"),
            label: String(event.label || "Event"),
            summary: String(event.summary || ""),
            summaryHtml: String(event.summaryHtml || ""),
            detail: String(event.detail || ""),
            status: String(event.status || ""),
            execution: event.execution === true,
            terminal: event.terminal === true
        }
    }

    function parseEvent(payload) {
        try {
            return normalizedEvent(JSON.parse(payload))
        } catch (error) {
            return normalizedEvent({ kind: "error", label: "Error", summary: String(error), status: "Error" })
        }
    }

    function parseEvents(payload) {
        try {
            var events = JSON.parse(payload)
            var result = []
            for (var i = 0; i < events.length; ++i) result.push(normalizedEvent(events[i]))
            return result
        } catch (error) {
            return [normalizedEvent({ kind: "error", label: "Error", summary: String(error), status: "Error" })]
        }
    }

    function resetEvents(events) {
        eventModel.clear()
        for (var i = 0; i < events.length; ++i) eventModel.append(events[i])
        Qt.callLater(function() { eventList.positionViewAtEnd() })
    }

    ListModel { id: eventModel }

    Connections {
        target: Backend
        function onEventsReset(payload) {
            window.showExecution = false
            window.resetEvents(window.parseEvents(payload))
        }
        function onEventAdded(payload) {
            eventModel.append(window.parseEvent(payload))
            Qt.callLater(function() { eventList.positionViewAtEnd() })
        }
        function onEventUpdated(index, payload) {
            if (index >= 0 && index < eventModel.count) {
                eventModel.set(index, window.parseEvent(payload))
                Qt.callLater(function() { eventList.positionViewAtEnd() })
            }
        }
    }

    Component.onCompleted: {
        var initial = []
        for (var i = 0; i < Backend.events.length; ++i) initial.push(window.normalizedEvent(Backend.events[i]))
        window.resetEvents(initial)
    }

    component SidebarButton: Button {
        id: control
        property bool primary: false
        implicitHeight: 38
        leftPadding: 12
        rightPadding: 12
        contentItem: Text {
            text: control.text
            color: control.enabled ? (control.primary ? "#ffffff" : fg) : "#a0a8b5"
            font.pixelSize: 13
            font.weight: control.primary ? Font.DemiBold : Font.Normal
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
        background: Rectangle {
            radius: 8
            color: !control.enabled ? "#f1f3f6" :
                   control.primary ? (control.hovered ? "#111827" : "#1f2329") :
                   control.hovered ? "#ffffff" : "#ffffff"
            border.color: control.primary ? "transparent" : (control.hovered ? "#cfd5df" : border)
        }
    }

    component SmallButton: Button {
        id: control
        implicitHeight: 30
        leftPadding: 9
        rightPadding: 9
        contentItem: Text {
            text: control.text
            color: control.enabled ? muted : "#a0a8b5"
            font.pixelSize: 12
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
        background: Rectangle {
            radius: 7
            color: control.hovered ? hoverBg : "transparent"
            border.color: control.hovered ? border : "transparent"
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.preferredWidth: 252
            Layout.minimumWidth: 236
            Layout.maximumWidth: 272
            Layout.fillHeight: true
            color: sidebarBg
            border.color: line

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 10

                Text {
                    text: "Code Agent"
                    color: titleFg
                    font.pixelSize: 24
                    font.bold: true
                    Layout.bottomMargin: 8
                }

                SidebarButton {
                    text: "新建项目"
                    Layout.fillWidth: true
                    enabled: !Backend.running
                    onClicked: Backend.newProject()
                }

                Text {
                    text: "项目"
                    color: faint
                    font.pixelSize: 12
                    font.weight: Font.DemiBold
                    Layout.topMargin: 10
                }

                ListView {
                    id: projectList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.preferredHeight: 150
                    model: Backend.projects
                    spacing: 3
                    clip: true
                    delegate: Rectangle {
                        width: projectList.width
                        height: 38
                        radius: 8
                        color: modelData.id === Backend.currentProjectId ? selectedBg : projectMouse.containsMouse ? hoverBg : "transparent"
                        border.color: modelData.id === Backend.currentProjectId ? selectedBorder : "transparent"
                        Text {
                            anchors.fill: parent
                            anchors.leftMargin: 11
                            anchors.rightMargin: 11
                            text: modelData.name
                            color: titleFg
                            font.pixelSize: 13
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                        }
                        MouseArea {
                            id: projectMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            enabled: !Backend.running
                            onClicked: Backend.selectProject(modelData.id)
                        }
                    }
                }

                Text {
                    text: "对话"
                    color: faint
                    font.pixelSize: 12
                    font.weight: Font.DemiBold
                    Layout.topMargin: 6
                }

                SidebarButton {
                    text: "新建对话"
                    Layout.fillWidth: true
                    primary: true
                    enabled: !Backend.running
                    onClicked: Backend.newChat()
                }

                ListView {
                    id: chatList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.preferredHeight: 230
                    model: Backend.chats
                    spacing: 3
                    clip: true
                    delegate: Rectangle {
                        width: chatList.width
                        height: 38
                        radius: 8
                        color: modelData.id === Backend.currentChatId ? selectedBg : chatMouse.containsMouse ? hoverBg : "transparent"
                        border.color: modelData.id === Backend.currentChatId ? selectedBorder : "transparent"
                        Text {
                            anchors.fill: parent
                            anchors.leftMargin: 11
                            anchors.rightMargin: 11
                            text: modelData.title
                            color: titleFg
                            font.pixelSize: 13
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                        }
                        MouseArea {
                            id: chatMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            enabled: !Backend.running
                            onClicked: Backend.selectChat(modelData.id)
                        }
                    }
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: line; Layout.topMargin: 8 }

                Text {
                    text: "运行设置"
                    color: faint
                    font.pixelSize: 12
                    font.weight: Font.DemiBold
                    Layout.topMargin: 8
                }

                Text {
                    text: "Workspace"
                    color: muted
                    font.pixelSize: 12
                    font.weight: Font.DemiBold
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 36
                    radius: 8
                    color: panelBg
                    border.color: border
                    Text {
                        anchors.fill: parent
                        anchors.leftMargin: 10
                        anchors.rightMargin: 10
                        text: Backend.workspace
                        color: "#4b5563"
                        font.pixelSize: 12
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideMiddle
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    SidebarButton {
                        text: Backend.selectedSkills.length > 0 ? "Skills: " + Backend.selectedSkills.length : "选择 Skills"
                        Layout.fillWidth: true
                        enabled: !Backend.running
                        onClicked: Backend.pickSkills()
                    }

                    Rectangle {
                        width: 92
                        height: 38
                        radius: 8
                        color: panelBg
                        border.color: border
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 3
                            spacing: 2
                            SmallButton {
                                text: "-"
                                enabled: !Backend.running && Backend.maxSteps > 1
                                onClicked: Backend.setMaxSteps(Backend.maxSteps - 1)
                            }
                            Text {
                                text: Backend.maxSteps
                                color: titleFg
                                font.pixelSize: 13
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                Layout.fillWidth: true
                            }
                            SmallButton {
                                text: "+"
                                enabled: !Backend.running && Backend.maxSteps < 30
                                onClicked: Backend.setMaxSteps(Backend.maxSteps + 1)
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: mainBg

            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                Rectangle {
                    Layout.fillWidth: true
                    height: 58
                    color: mainBg
                    border.color: line
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 24
                        anchors.rightMargin: 24
                        spacing: 12
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 1
                            Text {
                                text: Backend.currentChatTitle
                                color: titleFg
                                font.pixelSize: 17
                                font.bold: true
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        Text {
                            text: Backend.currentProjectName + " · " + Backend.model
                                color: muted
                                font.pixelSize: 12
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        }
                        SmallButton {
                            text: window.showExecution ? "隐藏过程" : "显示过程"
                            visible: eventModel.count > 0 && !Backend.running
                            onClicked: window.showExecution = !window.showExecution
                        }
                        Rectangle {
                            radius: 999
                            implicitWidth: statusLabel.implicitWidth + 24
                            implicitHeight: 28
                            color: Backend.running ? "#fff7ed" : "#eefaf5"
                            border.color: Backend.running ? "#fed7aa" : "#bde4d2"
                            Text {
                                id: statusLabel
                                anchors.centerIn: parent
                                text: Backend.status + " · Step " + Backend.step
                                color: Backend.running ? warning : success
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                            }
                        }
                    }
                }

                ListView {
                    id: eventList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    model: eventModel
                    clip: true
                    spacing: 0
                    leftMargin: 72
                    rightMargin: 72
                    topMargin: 22
                    bottomMargin: 22

                    delegate: Item {
                        id: row
                        width: eventList.width - eventList.leftMargin - eventList.rightMargin
                        readonly property string eventKind: model.kind || "event"
                        readonly property string eventLabel: model.label || "Event"
                        readonly property string eventSummary: model.summary || ""
                        readonly property string eventSummaryHtml: model.summaryHtml || ""
                        readonly property string eventDetail: model.detail || ""
                        readonly property string eventStatus: model.status || ""
                        readonly property bool eventExecution: model.execution === true
                        readonly property bool eventTerminal: model.terminal === true
                        readonly property bool isUser: eventKind === "user_message"
                        readonly property bool isExpanded: detailsToggle.checked
                        visible: Backend.running || window.showExecution || !row.eventExecution || row.eventKind === "finish" || row.eventKind === "error"
                        height: visible ? card.implicitHeight + 8 : 0

                        Rectangle {
                            id: card
                            width: row.isUser
                                   ? Math.min(parent.width, Math.max(260, Math.min(520, summaryText.implicitWidth + 44)))
                                   : Math.min(parent.width, 860)
                            x: row.isUser ? parent.width - width : 0
                            implicitHeight: bodyColumn.implicitHeight + 22
                            radius: 8
                            color: row.isUser ? "#eef1f6" :
                                   row.eventKind === "finish" ? "#ffffff" :
                                   row.eventKind === "error" ? "#fff1f2" : panelBg
                            border.color: row.eventKind === "error" ? "#fecdd3" :
                                          row.eventKind === "finish" ? "#d1d5db" : "#ebedf2"

                            ColumnLayout {
                                id: bodyColumn
                                anchors.fill: parent
                                anchors.margins: 11
                                spacing: 7

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    Text {
                                        text: row.eventLabel
                                        color: row.eventExecution ? accent : muted
                                        font.pixelSize: 12
                                        font.weight: Font.DemiBold
                                    }
                                    Item { Layout.fillWidth: true }
                                    Text {
                                        text: window.statusText(row.eventStatus, row.eventKind)
                                        visible: text.length > 0
                                        color: window.statusColor(row.eventStatus, row.eventKind)
                                        font.pixelSize: 12
                                        font.weight: Font.DemiBold
                                    }
                                    SmallButton {
                                        id: detailsToggle
                                        text: checked ? "收起详情" : "查看详情"
                                        checkable: true
                                        visible: row.eventDetail.length > 0 && row.eventKind !== "finish"
                                    }
                                }

                                Text {
                                    id: summaryText
                                    Layout.fillWidth: true
                                    text: row.eventSummaryHtml.length > 0 ? row.eventSummaryHtml : row.eventSummary
                                    color: fg
                                    wrapMode: Text.Wrap
                                    textFormat: row.eventSummaryHtml.length > 0 ? Text.RichText : Text.PlainText
                                    linkColor: accent
                                    onLinkActivated: function(link) { Qt.openUrlExternally(link) }
                                    font.pixelSize: 14
                                    font.family: row.eventTerminal ? "Courier New" : "Microsoft YaHei"
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    visible: row.isExpanded
                                    implicitHeight: row.isExpanded ? detailText.contentHeight + 20 : 0
                                    radius: 8
                                    color: row.eventTerminal ? "#111827" : "#f6f7f9"
                                    border.color: row.eventTerminal ? "#374151" : "#e1e5ec"
                                    TextEdit {
                                        id: detailText
                                        anchors.fill: parent
                                        anchors.margins: 10
                                        text: row.eventDetail
                                        readOnly: true
                                        selectByMouse: true
                                        wrapMode: TextEdit.Wrap
                                        color: row.eventTerminal ? "#e5e7eb" : titleFg
                                        font.family: "Courier New"
                                        font.pixelSize: 12
                                    }
                                }
                            }
                        }
                    }

                    Rectangle {
                        anchors.centerIn: parent
                        width: Math.min(640, parent.width - 120)
                        implicitHeight: emptyColumn.implicitHeight + 34
                        radius: 10
                        color: panelBg
                        border.color: "#e5e9f0"
                        visible: eventModel.count === 0
                        ColumnLayout {
                            id: emptyColumn
                            anchors.fill: parent
                            anchors.margins: 17
                            spacing: 8
                            Text {
                                text: "开始一个编码任务"
                                color: titleFg
                                font.pixelSize: 20
                                font.bold: true
                                Layout.fillWidth: true
                                horizontalAlignment: Text.AlignHCenter
                            }
                            Text {
                                text: "描述目标，Code Agent 会调用工具并实时展示执行过程。"
                                color: muted
                                font.pixelSize: 13
                                wrapMode: Text.Wrap
                                Layout.fillWidth: true
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 118
                    color: mainBg

                    Rectangle {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.leftMargin: 36
                        anchors.rightMargin: 36
                        anchors.topMargin: 4
                        height: 96
                        radius: 8
                        color: panelBg
                        border.color: input.activeFocus ? "#9aa8ff" : border

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 6

                            TextArea {
                                id: input
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                placeholderText: "给 Code Agent 一个编程任务..."
                                enabled: !Backend.running
                                wrapMode: TextArea.Wrap
                                selectByMouse: true
                                color: fg
                                placeholderTextColor: "#9aa3af"
                                font.pixelSize: 14
                                background: Rectangle { color: "transparent" }
                                Keys.onPressed: function(event) {
                                    if (event.key === Qt.Key_Return && (event.modifiers & Qt.ControlModifier)) {
                                        if (input.text.trim().length > 0 && !Backend.running) {
                                            Backend.runTask(input.text)
                                            input.text = ""
                                        }
                                        event.accepted = true
                                    }
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8
                                SmallButton {
                                    text: "+"
                                    enabled: !Backend.running
                                    onClicked: Backend.pickSkills()
                                }
                                Rectangle {
                                    visible: Backend.selectedSkills.length > 0
                                    Layout.maximumWidth: 260
                                    Layout.preferredWidth: Math.min(skillName.implicitWidth + 20, 260)
                                    height: 24
                                    radius: 7
                                    color: "#eef2ff"
                                    border.color: "#c7d2fe"
                                    Text {
                                        id: skillName
                                        anchors.fill: parent
                                        anchors.leftMargin: 9
                                        anchors.rightMargin: 9
                                        text: "Skills: " + Backend.selectedSkills.join(", ")
                                        color: accent
                                        font.pixelSize: 12
                                        font.weight: Font.DemiBold
                                        verticalAlignment: Text.AlignVCenter
                                        elide: Text.ElideRight
                                    }
                                }
                                Text {
                                    text: Backend.currentProjectName
                                    color: muted
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                    Layout.maximumWidth: 220
                                }
                                Text {
                                    text: Backend.model
                                    color: muted
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                    Layout.maximumWidth: 220
                                }
                                Item { Layout.fillWidth: true }
                                SidebarButton {
                                    text: "↑"
                                    primary: true
                                    width: 42
                                    implicitWidth: 42
                                    enabled: !Backend.running && input.text.trim().length > 0
                                    onClicked: {
                                        Backend.runTask(input.text)
                                        input.text = ""
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
