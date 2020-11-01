alter table "public"."baseline_project_assignees_timeline" drop constraint "baseline_project_assignees_timeline_pkey";
alter table "public"."baseline_project_assignees_timeline"
    add constraint "baseline_project_assignees_timeline_pkey" 
    primary key ( "id", "baseline_id", "project_id", "user_id" );
