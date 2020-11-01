ALTER TABLE "public"."calendar" ADD COLUMN "out_of_office" bool;
ALTER TABLE "public"."calendar" ALTER COLUMN "out_of_office" DROP NOT NULL;
ALTER TABLE "public"."calendar" ALTER COLUMN "out_of_office" SET DEFAULT false;
