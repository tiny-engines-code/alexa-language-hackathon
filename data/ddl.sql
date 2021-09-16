create table verbs.pronouns
(
	pronoun text,
	ordinal integer
);

alter table verbs.pronouns owner to postgres;

create table verbs.tenses
(
	tense text,
	modifier text,
	ordinal integer
);

alter table verbs.tenses owner to postgres;

create table verbs.conjugations
(
	conjugation_id serial not null
		constraint conjugations_pk
			primary key,
	verb text,
	tense text,
	pronoun text,
	conjugation text
);

alter table verbs.conjugations owner to postgres;

create table verbs.phrases
(
	phrase_id serial not null
		constraint phrases_pk
			primary key,
	verb text,
	phrase text
);

alter table verbs.phrases owner to postgres;

