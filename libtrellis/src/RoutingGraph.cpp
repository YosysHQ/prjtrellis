#include "RoutingGraph.h"

namespace Trellis {
ident_t RoutingGraph::ident(const std::string &str) const
{
    if (str_to_id.find(str) != str_to_id.end()) {
        return str_to_id.at(str);
    } else {
        str_to_id[str] = int(identifiers.size());
        identifiers.push_back(str);
        return str_to_id.at(str);
    }
}

std::string RoutingGraph::to_str(ident_t id) const
{
    return identifiers.at(id);
}

RoutingId RoutingGraph::id_at_loc(int16_t x, int16_t y, const std::string &str) const
{
    RoutingId rid;
    rid.id = ident(str);
    rid.loc = Location(x, y);
    return rid;
}


}
