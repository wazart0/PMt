ALTER TABLE "public"."calendar" ADD COLUMN "repeat_interval" interval;
ALTER TABLE "public"."calendar" ALTER COLUMN "repeat_interval" DROP NOT NULL;
