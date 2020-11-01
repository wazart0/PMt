ALTER TABLE "public"."calendar" ADD COLUMN "finish" timestamptz;
ALTER TABLE "public"."calendar" ALTER COLUMN "finish" DROP NOT NULL;
