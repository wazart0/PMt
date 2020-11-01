ALTER TABLE "public"."user_calendar" ADD COLUMN "created_at" timestamptz NOT NULL DEFAULT now();
