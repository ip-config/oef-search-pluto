#include <map>
#include <deque>
#include <utility>
#include <iostream>

using std::cout;
using std::endl;
using std::map;
using std::pair;
using std::deque;

class PopulationGrabber
{
public:

  struct Cell
  {
    int region;
    int population;

    int distance; // from region owner
  };

  struct Pending
  {
    int x;
    int y;
    int region;
    int distance;

    Pending(int x, int y, int r, int d)
    {
      this->x = x;
      this->y = y;
      this->region = r;
      this->distance = d;
    }
  };

  PopulationGrabber(int w,int h)
  {
    this->w = w;
    this->h = h;

    array = new Cell[w*h];

    memset(array, 0, w*h*sizeof(Cell));
  }

  virtual ~PopulationGrabber()
  {
    delete array;
  }


  void put(int id, int x, int y)
  {
    starts[id] = std::make_pair(x,y);
  }
  void remove(int id)
  {
    starts.erase(id);
  }

  void run()
  {
    clear_fill();
    clear_totals();

    fill();
    collect();
  }

  int get(int id)
  {
    auto iter = totals.find(id);
    if (iter != totals.end())
    {
      return iter->second;
    }
    return -1;
  }

  void set_pop(int x, int y, int population)
  {
    if (has(x,y))
    {
      access(x,y).population = population;
    }
  }

  int read_pop(int x,int y)
  {
    if (has(x,y))
    {
      return access(x,y).population;
    }
    return -1;
  }

  int read_reg(int x,int y)
  {
    if (has(x,y))
    {
      return access(x,y).region;
    }
    return -1;
  }

private:
  void fill()
  {
    deque<Pending> pending;
    for(auto kv : starts)
    {
      pending.push_back( Pending( kv.second.first, kv.second.second, kv.first, 0 ) );
    }

    int paint = 0;
    while(!pending.empty())
    {
      auto p = pending.front();
      pending.pop_front();

      auto there = access(p.x, p.y);

      if (
          (there.region == -1)
          ||
          (there.distance > p.distance)
          )
      {
        paint++;
        if ((paint % 10000) == 0)
        {
          cout << "Paint " << paint << "/" << w*h << " ... " << pending.size() << endl;
        }

        access(p.x, p.y).distance = p.distance;
        access(p.x, p.y).region = p.region;

        auto g = p.distance + 1;

        for(int i=-1;i<2;i++)
        {
          for(int j=-1;j<2;j++)
          {
            if (i==0 && j==0)
            {
              continue;
            }

            if (!has(p.x+i, p.y+j))
            {
              continue;
            }

            auto t = access(p.x+i, p.y+j);

            if (
                (t.region == -1)
                ||
                (t.distance > g)
                )
            {
              pending.push_back( Pending( p.x+i, p.y+j, p.region, g ) );
            }

          }
        }
      }
    }
  }

  void collect()
  {
    for(int i=0;i<w*h;i++)
    {
      totals[array[i].region] += array[i].population;
    }
  }

  void clear_fill()
  {
    for(int i=0;i<w*h;i++)
    {
      array[i].distance = 0;
      array[i].region = -1;
    }
  }

  void clear_totals()
  {
    totals.clear();
    for(auto kv : starts)
    {
      totals[kv.first] = 0;
    }
  }

  int w;
  int h;
  Cell *array;
  map<int, std::pair<int,int>> starts;
  map<int, int> totals;

  bool has(int x, int y) const { return x>=0 && x<w && y>=0 && y<w; }

  Cell &access(int x, int y) { return array[x + y*w ]; }
};
