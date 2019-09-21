ARG base_image
FROM $base_image as base

FROM nginx

COPY --from=base /staticfiles /usr/share/nginx/html/static
