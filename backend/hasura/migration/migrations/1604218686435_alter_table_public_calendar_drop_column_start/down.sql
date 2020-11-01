ALTER TABLE "public"."calendar" ADD COLUMN "start" timestamptz;
ALTER TABLE "public"."calendar" ALTER COLUMN "start" DROP NOT NULL;
