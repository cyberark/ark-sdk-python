---
title: Pagination
description: Pagination
---

# Pagination

## Motivation
When a request returns many items, or can be paginated and return pages of items, we paginate the request and return an iterator of pages instead of all the items

This is to not overload the request and wait for too long until a timeout, or just return a subset of the needed items

A request that does return a pagination response will return an Iterator of a page that contains an item
