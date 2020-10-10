CREATE TABLE public.baseline (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    name text NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    base_project_id uuid NOT NULL
);
CREATE TABLE public.baseline_project (
    baseline_id uuid NOT NULL,
    project_id uuid NOT NULL,
    parent_id uuid,
    start timestamp with time zone,
    finish timestamp with time zone,
    worktime interval
);
CREATE TABLE public.baseline_project_assignees_timeline (
    baseline_id uuid NOT NULL,
    project_id uuid NOT NULL,
    user_id uuid NOT NULL,
    start timestamp with time zone NOT NULL,
    finish timestamp with time zone NOT NULL,
    id bigint NOT NULL
);
CREATE SEQUENCE public.baseline_project_assignees_timeline_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.baseline_project_assignees_timeline_id_seq OWNED BY public.baseline_project_assignees_timeline.id;
CREATE TABLE public.baseline_project_dependency (
    baseline_id uuid NOT NULL,
    project_id uuid NOT NULL,
    predecessor_id uuid NOT NULL,
    type character varying DEFAULT 'FS'::character varying NOT NULL
);
CREATE TABLE public.calendar (
    id uuid NOT NULL,
    start timestamp with time zone NOT NULL,
    finish timestamp with time zone,
    "interval" interval,
    repeat_interval interval,
    out_of_office boolean DEFAULT false NOT NULL,
    name text NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);
CREATE TABLE public.project (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    name text NOT NULL,
    description text,
    id_num integer NOT NULL,
    label text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    default_baseline_id uuid
);
CREATE SEQUENCE public.project_no_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.project_no_id_seq OWNED BY public.project.id_num;
CREATE TABLE public."user" (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    email character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);
ALTER TABLE ONLY public.baseline_project_assignees_timeline ALTER COLUMN id SET DEFAULT nextval('public.baseline_project_assignees_timeline_id_seq'::regclass);
ALTER TABLE ONLY public.project ALTER COLUMN id_num SET DEFAULT nextval('public.project_no_id_seq'::regclass);
ALTER TABLE ONLY public.baseline
    ADD CONSTRAINT baseline_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.baseline_project_assignees_timeline
    ADD CONSTRAINT baseline_project_assignees_timeline_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.baseline_project_dependency
    ADD CONSTRAINT baseline_project_dependency_pkey PRIMARY KEY (baseline_id, project_id, predecessor_id);
ALTER TABLE ONLY public.baseline_project
    ADD CONSTRAINT baseline_project_pkey PRIMARY KEY (baseline_id, project_id);
ALTER TABLE ONLY public.calendar
    ADD CONSTRAINT calendar_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_no_id_key UNIQUE (id_num);
ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public."user"
    ADD CONSTRAINT users_email_key UNIQUE (email);
ALTER TABLE ONLY public."user"
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.baseline
    ADD CONSTRAINT baseline_base_project_id_fkey FOREIGN KEY (base_project_id) REFERENCES public.project(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.baseline_project
    ADD CONSTRAINT baseline_project_baseline_id_fkey FOREIGN KEY (baseline_id) REFERENCES public.baseline(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.baseline_project_dependency
    ADD CONSTRAINT baseline_project_dependency_baseline_id_fkey FOREIGN KEY (baseline_id) REFERENCES public.baseline(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.baseline_project_dependency
    ADD CONSTRAINT baseline_project_dependency_predecessor_id_fkey FOREIGN KEY (predecessor_id) REFERENCES public.project(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.baseline_project_dependency
    ADD CONSTRAINT baseline_project_dependency_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.project(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.baseline_project
    ADD CONSTRAINT baseline_project_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.project(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.baseline_project
    ADD CONSTRAINT baseline_project_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.project(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_default_baseline_id_fkey FOREIGN KEY (default_baseline_id) REFERENCES public.baseline(id) ON UPDATE RESTRICT ON DELETE SET NULL;
