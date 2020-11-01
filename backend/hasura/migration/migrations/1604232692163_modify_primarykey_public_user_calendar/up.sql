alter table "public"."user_calendar" drop constraint "user_calendar_pkey";
alter table "public"."user_calendar"
    add constraint "user_calendar_pkey" 
    primary key ( "user_id", "id" );
