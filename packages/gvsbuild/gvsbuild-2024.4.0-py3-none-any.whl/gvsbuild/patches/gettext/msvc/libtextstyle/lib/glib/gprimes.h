/* DO NOT EDIT! GENERATED AUTOMATICALLY! */
/* GLIB - Library of useful routines for C programming
 * Copyright (C) 2006-2019 Free Software Foundation, Inc.
 *
 * This file is not part of the GNU gettext program, but is used with
 * GNU gettext.
 *
 * The original copyright notice is as follows:
 */

/* GLIB - Library of useful routines for C programming
 * Copyright (C) 1995-1997  Peter Mattis, Spencer Kimball and Josh MacDonald
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public
 * License as published by the Free Software Foundation; either
 * version 3 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

/*
 * Modified by the GLib Team and others 1997-2000.  See the AUTHORS
 * file for a list of people on the GLib Team.  See the ChangeLog
 * files for a list of changes.  These files are distributed with
 * GLib at ftp://ftp.gtk.org/pub/gtk/. 
 */

/*
 * Modified by Bruno Haible for use as a gnulib module.
 */

#ifndef __G_PRIMES_H__
#define __G_PRIMES_H__

#include <glib/gtypes.h>

G_BEGIN_DECLS

/* Prime numbers.
 */

/* This function returns prime numbers spaced by approximately 1.5-2.0
 * and is for use in resizing data structures which prefer
 * prime-valued sizes.	The closest spaced prime function returns the
 * next largest prime, or the highest it knows about which is about
 * MAXINT/4.
 */
guint	   g_spaced_primes_closest (guint num) G_GNUC_CONST;

G_END_DECLS

#endif /* __G_PRIMES_H__ */
