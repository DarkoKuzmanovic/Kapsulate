import sys
import argparse
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtDBus import QDBusConnection, QDBusMessage, QDBusInterface

def trigger_action(action_name, extra_args=None):
    # Map friendly names to DBus methods
    methods = {
        "task-manager": "TriggerTaskManager",
        "color-picker": "TriggerColorPicker",
        "password": "TriggerPassword",
        "expand": "TriggerExpand",
        "transform": "TriggerTransform"
    }

    if action_name not in methods:
        print(f"Unknown action: {action_name}")
        sys.exit(1)

    method = methods[action_name]
    interface_name = "local.py.main.KapsulateService"
    
    msg = QDBusMessage.createMethodCall(
        "org.kapsulate.service",
        "/org/kapsulate/Service",
        interface_name,
        method
    )
    
    if action_name == "transform" and extra_args:
        # Pass the mode (upper, lower, etc)
        msg.setArguments([extra_args[0]])

    reply = QDBusConnection.sessionBus().call(msg)
    if reply.type() == QDBusMessage.MessageType.ErrorMessage:
        print(f"Error: {reply.errorMessage()}")
        sys.exit(1)
    else:
        print(f"Triggered {action_name}")

def main():
    app = QCoreApplication(sys.argv)
    parser = argparse.ArgumentParser(description="Kapsulate CLI Controller")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    trigger_parser = subparsers.add_parser("trigger", help="Trigger an action")
    trigger_parser.add_argument("action", choices=["task-manager", "color-picker", "password", "expand", "transform"], help="Action to trigger")
    trigger_parser.add_argument("args", nargs="*", help="Extra arguments for the action")

    args = parser.parse_args()

    if args.command == "trigger":
        trigger_action(args.action, args.args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
