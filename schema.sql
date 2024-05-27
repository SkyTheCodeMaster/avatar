SELECT 'CREATE DATABASE avatar' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'avatar')\gexec

\c avatar

CREATE TABLE IF NOT EXISTS Users (
  Name TEXT NOT NULL,
  Email TEXT, -- This is only filled if the user has Gravatar selected, and is the hash for gravatar.
              -- Gravatar uses trimmed, lowercase, sha256 as the hash.
  AvatarType INT, -- 0: Default
                  -- 1: URL
                  -- 2: Gravatar
                  -- 3: Retro
                  -- 4: Identicon
                  -- 5: MonsterID
                  -- 6: Wavatar
                  -- 7: Robohash

  AvatarURL TEXT,   -- Only used if AvatarType is 2.
  PRIMARY KEY (Name)
);

CREATE TABLE IF NOT EXISTS Avatars ( -- These avatars are hosted under /img/ for when users upload avatars.
  Username TEXT,
  Data BYTEA
);