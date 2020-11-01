ALTER TABLE "public"."calendar" ADD COLUMN "in_office" bool;
ALTER TABLE "public"."calendar" ALTER COLUMN "in_office" DROP NOT NULL;
ALTER TABLE "public"."calendar" ALTER COLUMN "in_office" SET DEFAULT true;
