import Alpine from "alpinejs";
import CTFd from "./index";
import eventStatus from "./theme/event-status";

window.CTFd = CTFd;
window.Alpine = Alpine;

eventStatus();

Alpine.start();
