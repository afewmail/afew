afew x.x (xxxx-xx-xx)
=====================

Filter behaviour change

  As of commit d98a0cd0d1f37ee64d03be75e75556cff9f32c29, the ListMailsFilter
  does not add a tag named `list-id `anymore, but a new one called
  `lists/<list-id>`.

afew 0.1pre (2012-02-10)
========================

Configuration format change

  Previously the values for configuration entries with the key `tags`
  were interpreted as a whitespace delimited list of strings. As of
  commit e4ec3ced16cc90c3e9c738630bf0151699c4c087 those entries are
  split at semicolons (';').

  This changes the semantic of the configuration file and affects
  everyone who uses filter rules that set or remove more than one tag
  at once. Please inspect your configuration files and adjust them if
  necessary.
