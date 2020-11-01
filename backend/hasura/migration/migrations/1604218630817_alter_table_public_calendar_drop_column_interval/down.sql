ALTER TABLE "public"."calendar" ADD COLUMN "interval" interval;
ALTER TABLE "public"."calendar" ALTER COLUMN "interval" DROP NOT NULL;
