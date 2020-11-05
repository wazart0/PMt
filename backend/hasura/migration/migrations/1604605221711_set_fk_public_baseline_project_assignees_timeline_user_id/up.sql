alter table "public"."baseline_project_assignees_timeline"
           add constraint "baseline_project_assignees_timeline_user_id_fkey"
           foreign key ("user_id")
           references "public"."user"
           ("id") on update restrict on delete restrict;
