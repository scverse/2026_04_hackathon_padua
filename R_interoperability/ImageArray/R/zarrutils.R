#' create_zarr_group
#'
#' Create a zarr group
#'
#' @param store the location of (zarr) store
#' @param name name of the group
#' @param version zarr version
#'
#' @return `NULL`
#'
#' @export
#'
#' @examples
#' store <- tempfile(fileext = ".zarr")
#' create_zarr(store)
#' create_zarr_group(store, "gp")
create_zarr_group <- function(store, name, version = "v2") {
  # check store and name
  if (!is.character(store)) {
    stop("'store' should be a valid zarr store name!")
  }
  if (!is.character(name)) {
    stop("'name' should be a valid zarr group name!")
  }

  # process paths, collapse repeating slashes
  name <- .collapse_slashes(name)
  name <- .check_group_name(store, name)

  # create group(s), split by "/"
  split_name <- strsplit(name, split = "/", fixed = TRUE)[[1]]

  # check names
  if (length(split_name) == 0) {
    stop("'name' should be a valid zarr group name!")
  }

  # create parent groups first, if supposed to exist
  if (length(split_name) > 1) {
    split_name <- vapply(
      seq_along(split_name),
      function(x) paste(split_name[seq_len(x)], collapse = "/"),
      FUN.VALUE = character(1)
    )
    split_name <- rev(tail(split_name, 2))
    if (!dir.exists(file.path(store, split_name[2]))) {
      create_zarr_group(store = store, name = split_name[2])
    }
  }

  # check and create zarr group
  dir.create(file.path(store, split_name[1]), showWarnings = FALSE)

  switch(
    version,
    v2 = {
      write(
        "{\"zarr_format\":2}",
        file = file.path(store, split_name[1], ".zgroup")
      )
    },
    v3 = {
      stop("Currently only zarr v2 is supported!")
    },
    stop("Only zarr v2 is supported. Use version = 'v2'")
  )
}

#' create_zarr
#'
#' Create zarr store
#'
#' @param store the location of zarr store
#' @param version zarr version
#'
#' @return `NULL`
#'
#' @export
#'
#' @examples
#' store <- tempfile(fileext = ".zarr")
#' create_zarr(store)
create_zarr <- function(store, version = "v2") {
  create_zarr_group(store = store, name = "/", version = version)
}

#' @noRd
.check_group_name <- function(store, name) {
  # group names with '.', or '..'
  if (name %in% c(".", "..")) {
    stop("Group name cannot be '.' or '..'")
  }

  # root group (already exists, must not be created)
  if (name %in% c("", "/")) {
    if (dir.exists(store)) {
      message("A group exists at path '", file.path(store, name), "'")
    }
    "/"
  } else {
    name
  }
}

#' Zarr path exists
#'
#' Check if a path in Zarr exists
#'
#' @return Whether the `name` exists in `store`
#' @noRd
#'
#' @param store Path to a Zarr store
#' @param name The path within the store to test for
.zarr_path_exists <- function(store, name = "") {
  zarr <- file.path(store, name)
  if (!dir.exists(zarr)) {
    FALSE
  } else {
    list_files <- list.files(
      path = zarr,
      full.names = FALSE,
      recursive = FALSE,
      all.files = TRUE
    )
    if (any(c(".zarray", ".zattrs", ".zgroup") %in% list_files)) {
      TRUE
    } else {
      FALSE
    }
  }
}
