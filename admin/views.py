from sqladmin import ModelView
from models.user import Master
from models.booking import Booking
from models.service import Service
from models.schedule import WorkSchedule


class MasterAdmin(ModelView, model=Master):
    name = "Мастер"
    name_plural = "Мастера"
    icon = "fa-solid fa-user"
    column_list = [
        Master.id,
        Master.name,
        Master.phone,
        Master.is_active,
        Master.created_at,
    ]
    column_searchable_list = [Master.id, Master.phone]
    column_sortable_list = [Master.id, Master.created_at]
    can_delete = True
    can_edit = True


class BookingAdmin(ModelView, model=Booking):
    name = "Запись"
    name_plural = "Записи"
    icon = "fa-solid fa-calendar"
    column_list = [
        Booking.id,
        Booking.client_name,
        Booking.client_phone,
        Booking.datetime_start,
        Booking.status,
        Booking.master_id,
    ]
    column_searchable_list = [Booking.client_name, Booking.client_phone]
    column_sortable_list = [Booking.id, Booking.datetime_start, Booking.status]
    can_delete = True
    can_edit = True


class ServiceAdmin(ModelView, model=Service):
    name = "Услуга"
    name_plural = "Услуги"
    icon = "fa-solid fa-scissors"
    column_list = [
        Service.id,
        Service.name,
        Service.duration,
        Service.price,
        Service.is_active,
        Service.master_id,
    ]
    can_delete = True
    can_edit = True


class ScheduleAdmin(ModelView, model=WorkSchedule):
    name = "Расписание"
    name_plural = "Расписание"
    icon = "fa-solid fa-clock"
    column_list = [
        WorkSchedule.id,
        WorkSchedule.weekday,
        WorkSchedule.start_time,
        WorkSchedule.end_time,
        WorkSchedule.is_working,
        WorkSchedule.master_id,
    ]
    can_delete = True
    can_edit = True
