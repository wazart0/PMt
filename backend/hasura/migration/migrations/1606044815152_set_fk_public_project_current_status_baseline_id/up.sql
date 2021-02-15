alter table "public"."project"
           add constraint "project_current_status_baseline_id_fkey"
           foreign key ("current_status_baseline_id")
           references "public"."baseline"
           ("id") on update restrict on delete restrict;
