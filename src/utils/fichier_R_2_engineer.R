
library(readxl)
library(tibble)
library(dplyr)
library(stringr)
library(stringi)      # pour enlever les accents
library(fuzzyjoin)

# --- 1) Import ---
data <- read_excel("calsseur_ivu.xlsx")  # adapte le nom si besoin

# --- 2) Pré-allocation & colonnes ---
n_prealloc <- 10000
new_data <- as_tibble(matrix("", nrow = n_prealloc, ncol = 6))
names(new_data) <- c("nom_client","annee","type_produit","nom_produit","quantite","prix")

idx_out <- 1  # pointeur d'écriture dans new_data

# indices colonnes source
col_client <- 1   # nom client
col_type   <- 4   # type / famille
col_prod   <- 5   # nom du produit
col_qte_2024  <- 6
col_prix_2024 <- 7
col_qte_2025  <- 8
col_prix_2025 <- 9

n_max <- nrow(data)

# --- 3) Boucle par bloc client ---
for (lines in 4:n_max) {

  v_cli <- data[[lines, col_client]]
  if (!is.na(v_cli)) {
    client_name <- as.character(v_cli)
    if (!startsWith(client_name, "Total")) {

      # Détection fin du bloc client
      number_of_lines <- 1
      while ((lines + number_of_lines) <= n_max &&
             (is.na(data[[lines + number_of_lines, col_client]]) ||
              startsWith(as.character(data[[lines + number_of_lines, col_client]]), "Total"))) {
        number_of_lines <- number_of_lines + 1
      }
      end_line <- min(lines + number_of_lines - 1, n_max)

      # ---- 3a) Collecte des lignes "type/famille" dans le bloc ----
      family_product <- character(0)  # libellés type
      list_val <- integer(0)          # indices de lignes où ces types apparaissent

      for (r in lines:end_line) {
        val_type <- as.character(data[[r, col_type]])
        if (!is.na(val_type) && nzchar(trimws(val_type)) && !startsWith(val_type, "Total")) {
          family_product <- c(family_product, val_type)
          list_val <- c(list_val, r)
        }
      }
      if (length(family_product) == 0) next

      names(family_product) <- list_val
      fam_idx <- as.integer(names(family_product))

      # ---- 3b) Pour chaque type : produits de la ligne du type jusqu'à la suivante ----
      for (k in seq_along(family_product)) {

        fam_label <- family_product[k]
        type_row  <- fam_idx[k]
        start_r   <- type_row                                # ⚠️ inclu la ligne du type
        stop_r    <- if (k < length(fam_idx)) fam_idx[k+1]-1 else end_line
        if (start_r > stop_r) next

        for (r in start_r:stop_r) {

          prod_name <- as.character(data[[r, col_prod]])
          if (is.na(prod_name) || !nzchar(trimws(prod_name)) || startsWith(prod_name, "Total")) next

          # ---------- Écriture 2024 ----------
          qte24  <- suppressWarnings(as.numeric(data[[r, col_qte_2024]]))
          prix24 <- suppressWarnings(as.numeric(data[[r, col_prix_2024]]))
          if (!is.na(qte24) || !is.na(prix24)) {
            new_data$nom_client[idx_out]   <- client_name
            new_data$annee[idx_out]        <- "2024"
            new_data$type_produit[idx_out] <- fam_label
            new_data$nom_produit[idx_out]  <- prod_name
            new_data$quantite[idx_out]     <- ifelse(is.na(qte24), 0, qte24)
            new_data$prix[idx_out]         <- ifelse(is.na(prix24), 0, prix24)
            idx_out <- idx_out + 1
          }

          # ---------- Écriture 2025 ----------
          qte25  <- suppressWarnings(as.numeric(data[[r, col_qte_2025]]))
          prix25 <- suppressWarnings(as.numeric(data[[r, col_prix_2025]]))
          if (!is.na(qte25) || !is.na(prix25)) {
            new_data$nom_client[idx_out]   <- client_name
            new_data$annee[idx_out]        <- "2025"
            new_data$type_produit[idx_out] <- fam_label
            new_data$nom_produit[idx_out]  <- prod_name
            new_data$quantite[idx_out]     <- ifelse(is.na(qte25), 0, qte25)
            new_data$prix[idx_out]         <- ifelse(is.na(prix25), 0, prix25)
            idx_out <- idx_out + 1
          }
        }
      }
    }
  }
}

# --- 4) Nettoyage final (trim la pré-allocation + types numériques) ---
if (idx_out > 1) {
  new_data <- new_data[1:(idx_out - 1), ]
} else {
  new_data <- new_data[0, ]
}

new_data <- new_data %>%
  mutate(
    quantite = suppressWarnings(as.numeric(quantite)),
    prix     = suppressWarnings(as.numeric(prix))
  )

# (Optionnel) aperçu
print(head(new_data, 12))
cat("Nombre de lignes finales :", nrow(new_data), "\n")

# (Optionnel) export
write.csv(new_data, "base_clean_2024_2025_avec_noms.csv", row.names = FALSE)




##### OK maintenant je traite les noms, à présent.
#je vais devoir créer des identifiant sur la base des clients puis ensuite faire un merge*
#ainsi j'aurait dans lma grosse base, l'identifiant et le noms du pays
#seulement ensuite je pourrais faire  une base avec client__france_1 etc

base_clients <- read_excel("base_clients.xlsx")

# Réorganisation des clients ----
base_clients <- base_clients %>%
  mutate(Noms = tolower(Noms) ) %>%
  arrange(Noms)

liste_clients_effectifs <-tolower(unique(sort(new_data$nom_client)))
liste_clients_dans_base <- base_clients$Noms

#il faut maintenant comparer ces deux listes.

n = length(liste_clients_effectifs)
p = length(liste_clients_dans_base)

n-p

liste_clients_dans_base_compl = c(liste_clients_dans_base,
                                  1:71)


#Comme il y a plus de clients dans la base des commandes que dans la base des clients
#je vais indexer les client directement sur la base des commanes

vecteur_client = liste_clients_effectifs
names(vecteur_client) = c(1:length(vecteur_client))
vecteur_id = names(vecteur_client)


names_df = data.frame(vecteur_client, vecteur_id)


#transformation du dataframe 1 pour mettre tous les noms en petit (minuscules)
new_data$nom_client <- tolower(new_data$nom_client)
new_data_id_miss_country  = merge(new_data,names_df, by.x = "nom_client", by.y = "vecteur_client" )


#Une fois que j'ai merger, j'ai ma base avec mes noms de client et mes id de clients.
#Il ne manque plus que merger avec la base de connées qui contient les noms et les pays
#ce qui va être beacoup plus compliquer.

normalize_name <- function(x) {
  x %>%
    # minuscules
    str_to_lower() %>%
    # enlever emails
    str_replace_all("\\S+@\\S+"," ") %>%
    # enlever tout ce qui est entre parenthèses
    str_replace_all("\\(.*?\\)", " ") %>%
    # couper à ":" et garder la partie avant (souvent commentaires après ":")
    { str_split_fixed(., ":", 2)[,1] } %>%
    # enlever accents
    stringi::stri_trans_general("Latin-ASCII") %>%
    # garder lettres/chiffres/espace uniquement
    str_replace_all("[^a-z0-9 ]", " ") %>%
    # réduire espaces multiples
    str_squish()
}

noms_normalises_base_pays  = normalize_name(liste_clients_dans_base)
noms_normalises_base_comm  = normalize_name(liste_clients_effectifs)


##trop compliquer donc à la main.......

#D'abord on regarde si on peut pas en créer un peu quand même
vec = liste_clients_dans_base %in% liste_clients_effectifs
table(vec)

#On voit alors qu'il y a 69 valeurs qui sont dans les deux liste, on va
#commencer en remplissant ces vecteurs là

new_data_id_miss_country$country <- "non renseigné"

for (i in 1:nrow(new_data)) {

  var_test = new_data_id_miss_country$nom_client[i]
  n = length(var_test)

  if (var_test %in% liste_clients_dans_base) {


    #chercher la donnée (l'indice) dans la base des clients
    #j'ai alors mon indice dans la base des client

    indice = which(base_clients$Noms==var_test)

    #et je peux assigner mon pays à la valeurs dans la basee base_client
    new_data_id_miss_country$country[i] <- base_clients$Pays[indice]

  }
}

#j'ai alors 69 pays renseigné automatiquement, on verra sur le reste à la main.
#nico et nikita m'aiderons.


new_dataa_confid_casi_complete <- new_data_id_miss_country

#creation de la base avec les clients cachés :
#Pour la prochaine fois seul --> création d'un vecteur hiden_names dans laquel
#je ferais une boucle et mettrai "client_"+"{nom_pays}" + "{numéro du client au sein du payus}(ex : client_france_3 si c'est la Troisieme client francais en partant du haut de ma base.)"

nrow(new_dataa_confid_casi_complete)
